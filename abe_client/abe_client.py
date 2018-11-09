import logging
import psycopg2
import json
import os
import base58
import time
import csv

class PostgreSQLInterface(object):

    def __init__(self, db_name, username, password, host=None, port=None):
        self._con = None
        self.db_name = db_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._connect_db()

    def _connect_db(self):
        if self._con is not None:
            return
        try:
            self._con = psycopg2.connect(user=self.username,
                                         password=self.password,
                                         dbname=self.db_name,
                                         host=self.host,
                                         port=self.port)
        except Exception, e:
            raise Exception("Error connecting to the database. error='%s'" % str(e))

    def _execute_query(self, query, params=None, fetch=True):
        self._connect_db()
        try:
            cursor = self._con.cursor()
            logging.debug(query)
            cursor.execute(query, params)
        except Exception, e:
            # We must reconnect to the database after an execute error occurred,
            #  because of the transaction incompleteness.
            self._con.close()
            self._con = None
            logging.exception("Error querying the server")
            raise Exception("Error querying the database %s . error='%s'" % (self.db_name, str(e)))
        if fetch:
            return cursor.fetchall()
        else:
            self._con.commit()
            
def btc_addr_to_hash(addr):
    return base58.b58decode_check(str(addr))[1:].encode("hex")
    
def btc_hash_to_addr(pk_hash):
    return base58.b58encode_check("\0" + str(pk_hash).decode("hex"))
            
class BTCTxOutput(object):
    """
    This is also used as input for other transactions
    """
    def __init__(self, value, pk_hash):
        #self.pos = pos
        self.value = value
        self.pk_hash = pk_hash
        
    def to_dict(self):
        return {"value": self.value, "pk_hash": self.pk_hash}
        
    @classmethod
    def from_dict(cls, d):
        return cls(d["value"], d["pk_hash"])
        
# class BTCTxInputSimple(object):
    # def __init__(self, value, pk_hash):
        # #self.pos = pos
        # self.value = value
        # self.pk_hash = pk_hash # The pk_hash from which this input gets its BTC value         
    
class BTCTransaction(object):
    def __init__(self, tx_hash, timestamp, inputs, outputs):
        self.tx_hash = tx_hash
        self.timestamp = int(timestamp)
        self.inputs = inputs
        self.outputs = outputs
        self.total_in = sum([input.value for input in self.inputs])
        self.total_out = sum([output.value for output in self.outputs])
        self.fee = self.total_in - self.total_out
        self.out_map = {}
        self.in_map = {}
        for output in self.outputs:
            self.out_map[output.pk_hash] = self.out_map.setdefault(output.pk_hash, 0) + output.value
        for input in self.inputs:
            self.in_map[input.pk_hash] = self.in_map.setdefault(input.pk_hash, 0) + input.value
        
    def get_all_out_pk_hashes(self):
        return set([output.pk_hash for output in self.outputs])
        
    def btc_to_usd(self, btc):
        btc_usd = find_btc_usd_rate_for_time(self.timestamp)
        return btc * btc_usd
        
    def stsh_to_usd(self, stsh):
        return self.btc_to_usd(float(stsh) / BTC_STSH)
        
    def usd_to_btc(self, usd):
        btc_usd = find_btc_usd_rate_for_time(self.timestamp)
        return usd / btc_usd
        
    def usd_to_stsh(self, usd):
        return self.usd_to_btc(usd) * BTC_STSH
        
    def to_dict(self):
        d = {}
        d["tx_hash"] = self.tx_hash
        d["ts"] = self.timestamp
        d["inputs"] = [input.to_dict() for input in self.inputs]
        d["outputs"] = [output.to_dict() for output in self.outputs]
        return d
        
    @classmethod
    def from_dict(cls, d):
        inputs = [BTCTxOutput.from_dict(e) for e in d["inputs"]]
        outputs = [BTCTxOutput.from_dict(e) for e in d["outputs"]]
        return cls(d["tx_hash"], d["ts"], inputs, outputs)
        
class BTCWallet(object):
    def __init__(self, pk_hash, input_txs, output_txs):
        self.pk_hash = pk_hash
        self.input_txs = input_txs
        self.output_txs = output_txs
        self.total_received = sum([tx.out_map[pk_hash] for tx in self.input_txs])
        self.total_spent = sum([tx.in_map[pk_hash] for tx in self.output_txs])
        self.remaining = self.total_received - self.total_spent
        
    def find_large_output_txs_btc(self, min_btc):
        results = []
        for tx in self.output_txs:
            if tx.in_map[self.pk_hash] > min_btc:
                results.append(tx)
        return results
        
    def find_large_output_txs_usd(self, min_usd):
        results = []
        for tx in self.output_txs:
            min_btc = tx.usd_to_stsh(min_usd)
            if tx.in_map[self.pk_hash] > min_btc:
                results.append(tx)
        return results        
        
    def to_dict(self):
        d = {}
        d["pk_hash"] = self.pk_hash
        d["input_txs"] = [tx.tx_hash for tx in self.input_txs]
        d["output_txs"] = [tx.tx_hash for tx in self.output_txs]
        return d
        
    @classmethod
    def from_dict(cls, d, tx_cache):
        input_txs = [tx_cache[tx_hash] for tx_hash in d["input_txs"]]
        output_txs = [tx_cache[tx_hash] for tx_hash in d["output_txs"]]
        return cls(d["pk_hash"], input_txs, output_txs)
        
                
class ABEPostgreSQLClient(PostgreSQLInterface):
    MAX_QUERY_ITEMS = 100
    
    def _req_generic_get_item_ids_by_hashes(self, item_hashes, item_name, table_name):
        query_res = []
        for i in xrange(0, len(item_hashes), self.MAX_QUERY_ITEMS):
            query = "SELECT %s_id, %s_hash FROM public.%s " \
                    "WHERE %s_hash in (%s)" % (item_name, item_name, table_name, item_name,
                        ",".join(["'%s'" % item_hash for item_hash in item_hashes[i:i+self.MAX_QUERY_ITEMS]]))
            query_res += self._execute_query(query)
        item_hashes_indices = {item_hash: i for i, item_hash in enumerate(item_hashes)}
        res = [0] * len(item_hashes)
        for item_id, item_hash in query_res:
            if not item_id or not item_hash:
                raise Exception("Couldn't find some item")
            res[item_hashes_indices[item_hash]] = int(item_id)
        return res
        
    def _req_generic_get_item_hashes_by_ids(self, item_ids, item_name, table_name):
        query_res = []
        for i in xrange(0, len(item_ids), self.MAX_QUERY_ITEMS):
            query = "SELECT %s_hash, %s_id FROM public.%s " \
                    "WHERE %s_id in (%s)" % (item_name, item_name, table_name, item_name, 
                        ",".join(["%s" % item_id for item_id in item_ids[i:i+self.MAX_QUERY_ITEMS]]))
            query_res += self._execute_query(query)
        item_ids_indices = {item_id: i for i, item_id in enumerate(item_ids)}
        res = [0] * len(item_ids)
        for item_hash, item_id in query_res:
            if not item_id or not item_hash:
                raise Exception("Couldn't find some item")
            res[item_ids_indices[int(item_id)]] = item_hash
        return res         
        
    def req_get_pubkey_ids_by_hashes(self, pk_hashes):
        """
        Translate BTC Pubkey hashes to ABE Pubkey IDs (pubkey_id)
        """
        return self._req_generic_get_item_ids_by_hashes(pk_hashes, "pubkey", "pubkey")
        
    def req_get_pubkey_hashes_by_ids(self, pk_ids):
        """
        Translate ABE Pubkey IDs (pubkey_id) to BTC Pubkey hashes
        """    
        return self._req_generic_get_item_hashes_by_ids(pk_ids, "pubkey", "pubkey")

    def req_get_tx_ids_by_hashes(self, tx_hashes):
        """
        Translate BTC transaction hashes to ABE transaction ids (tx_id)
        """
        return self._req_generic_get_item_ids_by_hashes(tx_hashes, "tx", "tx")
        
    def req_get_tx_hashes_by_ids(self, tx_ids):
        """
        Translate ABE transaction ids (tx_id) to BTC transaction hashes
        """    
        return self._req_generic_get_item_hashes_by_ids(tx_ids, "tx", "tx")
        
    def get_all_txins_for_tx(self, tx_id):
        """
        Get all inputs for the given transaction.
        Each input has an Id and a previous transaction's output Id, from which the BTC
        is retrieved.
        Returns list of (txin_id, txout_id)
        """
        res = self._execute_query("SELECT txin_id, txout_id FROM public.txin " 
                                  "WHERE tx_id = %d" % tx_id)
        return [map(int, r) for r in res]
        
    def get_all_txouts_for_tx(self, tx_id):
        """
        Get all outputs of the given transaction.
        Each output has an Id, value and target pubkey Id.
        (txout_id, txout_value, pubkey_id)
        """
        res = self._execute_query("SELECT txout_id, txout_value, pubkey_id FROM public.txout " 
                                  "WHERE tx_id = %d" % tx_id)
        return [map(int, r) for r in res]
        
        
    def req_get_all_txouts_for_pk(self, pk_id):
        """
        Get all transactions outputs in which the given pubkey is the target.
        This represents all incoming BTC to the given address.
        Returns list of (txout_id, tx_id, txout_value)
        """
        res = self._execute_query("SELECT txout_id, tx_id, txout_value FROM public.txout " 
                            "WHERE pubkey_id = %d" % pk_id)
        return [map(int, r) for r in res]
        
    def req_get_all_txins_for_txouts(self, txout_ids):
        """
        Get all transaction inputs using any of the given tx outputs.
        This represents all outgoing BTC from the BTC addresses that received BTC
        by the given tx outputs.
        Returns list of (txin_id, tx_id)
        """
        txout_ids = set(txout_ids)
        query = "SELECT txin_id, tx_id FROM public.txin " \
                "WHERE txout_id in (%s)" % (
                        ",".join(["'%s'" % txout_id for txout_id in txout_ids]))
        res = self._execute_query(query)
        return [map(int, r) for r in res]
        
    def req_get_txouts(self, txout_ids):
        """
        Get all transaction outputs related to the given txout_ids, in arbitrary order.
        returns list of (tx_id, txout_value, pubkey_id)
        """
        txout_ids = set(txout_ids)
        query = "SELECT tx_id, txout_value, pubkey_id FROM public.txout " \
                "WHERE txout_id in (%s)" % (
                        ",".join(["'%s'" % txout_id for txout_id in txout_ids]))
        res = self._execute_query(query)
        return [map(int, r) for r in res]
        
    def req_get_tx_block_id(self, tx_id):
        query = "SELECT block_id FROM public.block_tx " \
                "WHERE tx_id = %d" % tx_id
        return int(self._execute_query(query)[0][0])
        
    def req_get_block_timestamp(self, block_id):
        query = "SELECT block_ntime FROM public.block " \
                "WHERE block_id = %d" % block_id
        return int(self._execute_query(query)[0][0])        
        
        
    #def 
        
    #def _req_
        
    
    #def get_
    # def test1(self):
        # res = self._execute_query("SELECT * FROM public.txout "
                            # "WHERE txout_id = 3484961")
        # import code
        # code.interact(local=locals())
        
class BTCChainAnalyzer(object):
    def __init__(self, abe_client):
        self._client = abe_client
        self._pk_hash_to_id = {}
        self._tx_hash_to_id = {}
        self._pk_id_to_hash = {}
        self._tx_id_to_hash = {}
        self._txs = {}
        self._wallets = {}
        
    def save_state(self, fname):
        state = {}
        state["pk_hash_to_id"] = self._pk_hash_to_id
        state["tx_hash_to_id"] = self._tx_hash_to_id
        state["pk_id_to_hash"] = self._pk_id_to_hash
        state["tx_id_to_hash"] = self._tx_id_to_hash        
        state["txs"] = {tx_hash: tx.to_dict() for tx_hash, tx in self._txs.iteritems()}
        state["wallets"] = {pk_hash: wallet.to_dict() for pk_hash, wallet in self._wallets.iteritems()}
        json.dump(state, open(fname, "w"))
        
    def load_state(self, fname):
        state = json.load(open(fname, "r"))
        self._pk_hash_to_id = state.get("pk_hash_to_id", {})
        self._tx_hash_to_id = state.get("tx_hash_to_id", {})
        self._pk_id_to_hash = state.get("pk_id_to_hash", {})
        self._tx_id_to_hash = state.get("tx_id_to_hash", {})
        self._txs = state.get("txs", {})
        self._wallets = state.get("wallets", {})
        
        self._pk_id_to_hash = {int(i):h for i,h in self._pk_id_to_hash.iteritems()}
        self._tx_id_to_hash = {int(i):h for i,h in self._tx_id_to_hash.iteritems()}
        self._txs = {tx_hash: BTCTransaction.from_dict(d) for tx_hash, d in self._txs.iteritems()}
        self._wallets = {pk_hash: BTCWallet.from_dict(d, self._txs) for pk_hash, d in self._wallets.iteritems()}
        
        
    def _generic_get_ids_by_hashes(self, item_hashes, cache, fetch_func):
        single = False
        if not isinstance(item_hashes, (list, tuple)):
            item_hashes = (item_hashes,)
            single = True
        missing_hashes = {}
        #missing_indices = []
        results = [0] * len(item_hashes)
        for i, item_hash in enumerate(item_hashes):
            item_id = cache.get(item_hash)
            if item_id is None:
                missing_hashes.setdefault(item_hash, []).append(i)
                #missing_indices.append(i)
            else:
                results[i] = item_id
        if missing_hashes:
            missing_hashes_keys = missing_hashes.keys()
            fetched_ids = fetch_func(missing_hashes_keys)
            for i, fetched_id in enumerate(fetched_ids):
                missing_hash = missing_hashes_keys[i]
                if not fetched_id:
                    raise Exception("Couldn't find %s" % missing_hash)
                for j in missing_hashes[missing_hash]:
                    results[j] = fetched_id
                cache[missing_hash] = fetched_id
        if single:
            return results[0]
        return results        
        
    def get_pk_ids(self, pk_hashes):
        return self._generic_get_ids_by_hashes(pk_hashes, self._pk_hash_to_id, self._client.req_get_pubkey_ids_by_hashes)

    def get_tx_ids(self, tx_hashes):
        return self._generic_get_ids_by_hashes(tx_hashes, self._tx_hash_to_id, self._client.req_get_tx_ids_by_hashes)

    def get_pk_hashes(self, pk_ids):
        return self._generic_get_ids_by_hashes(pk_ids, self._pk_id_to_hash, self._client.req_get_pubkey_hashes_by_ids)

    def get_tx_hashes(self, tx_ids):
        return self._generic_get_ids_by_hashes(tx_ids, self._tx_id_to_hash, self._client.req_get_tx_hashes_by_ids)
                
    # def get_inputs_for_pk(self, pk_hash):
        # pk_id = self.get_pk_ids(pk_hash)
        # txouts = self._client.req_get_all_txouts_for_pk(pk_id)
        # txout_id, txout_value
        
    # def get_txouts_by_addr(self, pk_hash):
        # pk_id = self.get_pk_ids(pk_hash)
        # # First get all txouts into the given PK, so we can follow them.
        # txouts = self._client.req_get_all_txouts_for_pk(pk_id)
        # total_
        # self._client.req_get_all_txins_for_txouts()
        
    def _learn_transaction(self, tx_id):
        try:
            tx_hash = self.get_tx_hashes(tx_id)
        except Exception, e:
            raise Exception("Failed to learn transaction Id %s: %s" % (tx_id, str(e)))
            
        block_id = self._client.req_get_tx_block_id(tx_id)
        timestamp = self._client.req_get_block_timestamp(block_id)
            
        # Get inputs and ouputs for this transaction
        txins = self._client.get_all_txins_for_tx(tx_id)
        txouts = self._client.get_all_txouts_for_tx(tx_id)
        # The inputs themselves don't contain the origin and the amount, but just 
        # the IDs of the outputs of older txs that were used. So go one step backwards
        # and get their BTC addrs and amounts.
        txinout_ids = [txin[1] for txin in txins if txin[1]]
        txinouts = self._client.req_get_txouts(txinout_ids)
        
        txout_pk_ids = [txout[2] for txout in txouts]
        txout_pk_hashes = self.get_pk_hashes(txout_pk_ids)
        outputs = []
        for i, (txout_id, value, pk_id) in enumerate(txouts):
            outputs.append(BTCTxOutput(value, txout_pk_hashes[i]))
            
        txinout_pk_ids = [txinout[2] for txinout in txinouts]
        txinout_pk_hashes = self.get_pk_hashes(txinout_pk_ids)
        inputs = []
        for i, (txout_id, value, pk_id) in enumerate(txinouts):
            inputs.append(BTCTxOutput(value, txinout_pk_hashes[i]))
            
        return BTCTransaction(tx_hash, timestamp, inputs, outputs)
        
    def _learn_wallet(self, pk_hash):
        try:
            pk_id = self.get_pk_ids(pk_hash)
        except Exception, e:
            raise Exception("Error learning wallet %s: %s" % (pk_hash, str(e)))
            
        # First get all transactions that have an output into this wallet.
        txouts = self._client.req_get_all_txouts_for_pk(pk_id)
        logging.info("Wallet %s has %d txouts" % (pk_hash, len(txouts)))
        input_tx_ids = set([tx_id for txout_id, tx_id, txout_value in txouts])
        input_txs = []
        for input_tx_id in input_tx_ids:
            input_txs.append(self.get_tx_by_id(input_tx_id))

        # Find out which one of the incoming txouts were used later as output.
        
        # Track all outgoing transactions
        txout_ids = set([txout_id for txout_id, tx_id, txout_value in txouts])
        txins = self._client.req_get_all_txins_for_txouts(txout_ids)
        output_tx_ids = [tx_id for txin_id, tx_id in txins]
        output_txs = []
        for output_tx_id in output_tx_ids:
            output_txs.append(self.get_tx_by_id(output_tx_id))
        
        wallet = BTCWallet(pk_hash, input_txs, output_txs)
        return wallet
        
    def get_tx_by_id(self, tx_id):
        tx_hash = self.get_tx_hashes(tx_id)
        tx = self._txs.get(tx_hash, None)
        if tx is None:
            tx = self._learn_transaction(tx_id)
            self._txs[tx_hash] = tx
        return tx        

        
    def get_wallet(self, pk_hash):
        wallet = self._wallets.get(pk_hash, None)
        if wallet is None:
            wallet = self._learn_wallet(pk_hash)
            self._wallets[pk_hash] = wallet
        return wallet

    #def find_all_tx_for_pk(self, pk_hash):
    #    self._client.
    
class BTCDirtyAddress(object):
    def __init__(self, pk_hash, ):
        pass
    
BTC_STSH = 100000000

class BTCDirtyAddrFollowerBase(object):    
    def __init__(self, analyzer):
        self._analyzer = analyzer
        self._dirty_addrs = {}
        #self.
        
    def save_state(self, fname):
        state = self._dirty_addrs
        json.dump(state, open(fname, "w"))
        
    def load_state(self, fname):
        state = json.load(open(fname, "r"))
        self._dirty_addrs = state
        
    def get_unprocessed_addrs(self):
        addrs = set()
        for addr, data in self._dirty_addrs.iteritems():
            infection_data = data.get("infection_data", {})
            processed = infection_data.get("processed", False)
            if not processed:
                addrs.add(addr)
        return addrs
        
    def add_infected_addr(self, addr_or_hash, infected_by, **kwargs):
        if len(addr_or_hash) == 40:
            addr = btc_hash_to_addr(addr_or_hash)
        else:
            addr = addr_or_hash
        # TODO: Support multiple infections
        if self._dirty_addrs.has_key(addr):
            return
        
        infection_data = {}
        infection_data["processed"] = False
        if len(infected_by) == 40:
            infected_by_hash = infected_by
            infected_by_addr = btc_hash_to_addr(infected_by_hash)
        else:
            infected_by_addr = infected_by
            infected_by_hash = btc_addr_to_hash(infected_by_addr)
        infection_data["infected_by_addr"] = infected_by_addr
        infection_data["infected_by_hash"] = infected_by_hash
        infection_data.update(kwargs)
        self._dirty_addrs[addr] = {"infection_data": infection_data}
        
    def process_all_unprocessed_addrs(self):
        addrs = self.get_unprocessed_addrs()
        logging.info("We have %d unprocessed dirty addrs" % len(addrs))
        for addr in addrs:
            try:
                self.process_addr(addr)
            except Exception, e:
                #import traceback
                #traceback.print_exc()
                logging.error(str(e))        
                
    def process_addr(self, addr):
        logging.info("Processing dirty addr %s" % addr)
        data = self._dirty_addrs[addr]
        infection_data = data.setdefault("infection_data", {"processed": False})
        pk_hash = btc_addr_to_hash(addr)
        try:
            wallet = self._analyzer.get_wallet(pk_hash)
        except Exception, e:
            infection_data["processed"] = "Error getting wallet: %s" % str(e)
            logging.error("Error processing addr %s: %s" % (addr, str(e)))
            return False
            
        try:
            self.process_wallet(wallet, infection_data)
        except Exception, e:    
            infection_data["processed"] = "Error processing wallet: %s" % str(e)
            return False
        infection_data["processed"] = True
        return True
        
    def process_wallet(self, wallet, infection_data):
        pass
        
class BTCDirtyAddrFollower_BasicThreshold(BTCDirtyAddrFollowerBase):
    #MINIMUM_DIRTY_AMOUNT = 1000 * BTC_STSH
    MINIMUM_DIRTY_AMOUNT_USD = 12000.0
    
    def process_wallet(self, wallet, infection_data):
        txs = wallet.find_large_output_txs_usd(self.MINIMUM_DIRTY_AMOUNT_USD)
        all_infected_hashes = set()
        for tx in txs:
            infect_hashes = tx.get_all_out_pk_hashes()
            all_infected_hashes |= infect_hashes
            for inf_pk_hash in infect_hashes:
                amount_btc=tx.in_map[wallet.pk_hash]
                amount_usd=tx.stsh_to_usd(amount_btc)
                self.add_infected_addr(inf_pk_hash, wallet.pk_hash, 
                                        amount_btc=amount_btc, amount_usd=amount_usd)
        if all_infected_hashes:
            logging.warn("Infected new addrs: %s" % list(all_infected_hashes))
        
class BTCDirtyAddrFollower_WeightedWithInfectionThreshold(BTCDirtyAddrFollowerBase):
    def process_wallet(self, wallet, infection_data):
        return
        # txs = wallet.find_large_output_txs(self.MINIMUM_DIRTY_AMOUNT)
        # all_infected_hashes = set()
        # for tx in txs:
            # infect_hashes = tx.get_all_out_pk_hashes()
            # all_infected_hashes |= infect_hashes
            # for inf_pk_hash in infect_hashes:
                # self.add_infected_addr(inf_pk_hash, pk_hash, tx.in_map[pk_hash])
        # if all_infected_hashes:
            # logging.warn("Infected new addrs: %s" % list(all_infected_hashes))
            
def load_btc_usd_csv():
    rates = []
    with open('btc_to_usd.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for date_str, value in reader:
            timestamp = int(time.mktime(time.strptime(date_str,"%Y-%m-%d %H:%M:%S")))
            rates.append((timestamp, float(value)))
    return rates
          
def find_btc_usd_rate_for_time(ts):
    global g_btc_usd_rates
    lower = g_btc_usd_rates[0]
    loweri = 0
    upper = g_btc_usd_rates[-1] 
    upperi = len(g_btc_usd_rates) - 1
    while upperi - loweri != 1:
        #print upperi, loweri
        middlei = (loweri + upperi) / 2
        middle = g_btc_usd_rates[middlei]
        if ts < middle[0]:
            upperi = middlei
            upper = middle
        else:
            loweri = middlei
            lower = middle
    return (upper[1] + lower[1]) / 2.0
    
        
PK_HASH_1 = "90b7960f0ed9973adf2b32e37f40dfbf2c996acd"
PK_HASH_2 = "4988d2565fa600d22226b688e737e605bbe653c2"
PK_HASH_3 = "0dcd845e144d597a409b361f2e9da97cd6ffd18b"

TX_ID_1 = 932089  # 7c010d4d9af7054985eeb93831c90d2ad3411bf7e955d4c0fda5ec35e8f82142
TX_ID_2 = 2734847 # cfb3d67e76cc082a060948d955e7821b9db73a67b11e2725463f3df7c82ea5c0

TXIN_ID_1 = 1534611

TXOUT_ID_1 = 1868450
TXOUT_ID_2 = 1868451

ABE_CACHE_FNAME = "abe_cache.json"
DIRTY_ADDRS_FNAME1 = "dirty_addrs1.json"
DIRTY_ADDRS_FNAME2 = "dirty_addrs2.json"


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
        
def main(): 
    global g_btc_usd_rates
    g_btc_usd_rates = load_btc_usd_csv()
    c = ABEPostgreSQLClient("abe", "postgres", "btc", "localhost", 5432)
    # res = c.req_get_pubkey_ids_by_hashes([PK_HASH_1, PK_HASH_2, PK_HASH_3])
    # res2 = c.req_get_pubkey_hashes_by_ids(res)
    # assert res2 == [PK_HASH_1, PK_HASH_2, PK_HASH_3]
    # res3 = c.req_get_tx_hashes_by_ids([TX_ID_1, TX_ID_2])
    # res4 = c.req_get_tx_ids_by_hashes(res3)
    # assert res4 == [TX_ID_1, TX_ID_2]
    # res5 = c.req_get_all_txouts_for_pk(res[0])
    # res6 = c.req_get_all_txins_for_txouts([TXOUT_ID_1, TXOUT_ID_2])
    
    a = BTCChainAnalyzer(c)
    if os.path.isfile(ABE_CACHE_FNAME):
        a.load_state(ABE_CACHE_FNAME)
        
    a.get_pk_ids([PK_HASH_1, PK_HASH_2])

    f1 = BTCDirtyAddrFollower_BasicThreshold(a)
    f2 = BTCDirtyAddrFollower_WeightedWithInfectionThreshold(a)
    
    if os.path.isfile(DIRTY_ADDRS_FNAME1):
        f1.load_state(DIRTY_ADDRS_FNAME1)
        
    if os.path.isfile(DIRTY_ADDRS_FNAME2):
        f2.load_state(DIRTY_ADDRS_FNAME2)

    try:
        tx = a.get_tx_by_id(TX_ID_1)
        wallet = a.get_wallet(PK_HASH_1)
        f1.process_all_unprocessed_addrs()
        #f2.process_all_unprocessed_addrs()
        import code
        locs = locals()
        locs.update(globals())
        code.interact(local=locs)
    finally:
        print "Saving state"
        a.save_state(ABE_CACHE_FNAME)
        f1.save_state(DIRTY_ADDRS_FNAME1)
        f2.save_state(DIRTY_ADDRS_FNAME2)

if __name__ == "__main__":
    main()
