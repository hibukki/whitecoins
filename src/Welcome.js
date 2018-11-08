import React, { Component } from 'react';

class Welcome extends React.Component {
  

  render() {
    return (<div>

                <h1>The address {this.props.address} is {this.props.clean ? "clean" : "dirty"}</h1>
                <h2>Here is the chain of events:</h2>
                <div>{this.props.address} <a href="#">got</a> 2.7 BTC from 0x345346</div>
                <div>0x345346 <a href="#">got</a> 7.6 BTC from 0xdeadbeef</div>
                <div>0xdeadbeef is evil!</div>

                
                <h2>Here is the dirty info about the address 0xdeadbeef:</h2>
                <div>
                    <pre>
                    {
                        JSON.stringify({
                      "id": 6083,
                      "name": "myetherwalletmsg.com",
                      "url": "http://myetherwalletmsg.com",
                      "coin": "ETH",
                      "category": "Phishing",
                      "subcategory": "MyEtherWallet",
                      "description": "Fake MyEtherWallet phishing for keys with POST /store.php",
                      "reporter": "MyCrypto",
                      "ip": "142.11.192.161",
                      "nameservers": [
                        "ns83.hostwindsdns.com",
                        "ns84.hostwindsdns.com"
                      ],
                      "status": "Offline"
                    }, undefined, 2)
                    }
                    </pre>
                </div>

                <hr/>
                <h3>
                    When you trade with your friend, you're trading with your friends friend...
                </h3>
                <hr/>
                <div>Hello, {this.props.name}</div>
                <a onClick={() => this.props.foofunc()}> click me! </a>
            </div>);
  }
}

export default Welcome;