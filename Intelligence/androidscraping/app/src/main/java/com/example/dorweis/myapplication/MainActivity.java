package com.example.dorweis.myapplication;

import android.content.Context;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Cache;
import com.android.volley.Network;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.BasicNetwork;
import com.android.volley.toolbox.DiskBasedCache;
import com.android.volley.toolbox.HurlStack;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.gson.Gson;


import org.json.JSONArray;
import org.json.JSONObject;
import org.yaml.snakeyaml.Yaml;

import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    public static final String ADDRESS = "adrresssdf";
    Button btn;
    Button savebtn;
    TextView tv;
    Handler handler;
    RequestQueue mRequestQueue;  // Assume this exists.
    String url ="https://etherscamdb.info/api/scams";
    RequestQueue queue;

    @Override
    protected void onResume() {
        super.onResume();

    }

    @Override
    protected void onPause() {
        super.onPause();

    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        queue = Volley.newRequestQueue(this);

// Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap

// Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());

// Instantiate the RequestQueue with the cache and network.
        mRequestQueue = new RequestQueue(cache, network);

        mRequestQueue.start();
        btn = (Button) findViewById(R.id.btn);
        tv = (TextView) findViewById(R.id.tv);
        handler = new Handler();

        btn.setOnClickListener(this);

    }

    private void savetofile(String s) {

        try {
            OutputStreamWriter outputStreamWriter = new OutputStreamWriter(openFileOutput("primeblacks.json", Context.MODE_PRIVATE));
            outputStreamWriter.write(s);
            outputStreamWriter.close();
        }
        catch (IOException e) {
            Log.e("Exception", "File write failed: " + e.toString());
        }
    }

    @Override
    public void onClick(View v) {
        final Gson gson = new Gson();
        jsonObjectRequest(gson);



    }
    @Override
    protected void onStop () {
        super.onStop();
        if (mRequestQueue != null) {
            mRequestQueue.cancelAll("canceled");
        }
    }

    private static String convertToJson(String yamlString) {
        Yaml yaml= new Yaml();
        Map<String,Object> map= (Map<String, Object>) yaml.load(yamlString);

        JSONObject jsonObject=new JSONObject(map);
        return jsonObject.toString();
    }

    private void jsonObjectRequest(final Gson gson){
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {

                    @Override
                    public void onResponse(JSONObject response) {
                        try {

                            HashMap<String,ScamObject> hashMapObjects = new HashMap<>();
                            String coin = null;
                            String name = null;
                            String url = null;
                            String category = null;
                            String subcategory = null;
                            String description = null;
                            String reporter = null;
                            String ip = null;
                            String status = null;
                            JSONArray nameservers = null;
                            JSONArray addresses = null;
                            int id = 1;

                            JSONArray jsonResults = response.getJSONArray("result");


                            for (int i = 0; i < jsonResults.length(); i++) {
                                nameservers = null;
                                addresses = null;

                                JSONObject dataObj = jsonResults.getJSONObject(i);
                                if (dataObj.has("coin") && dataObj.get("coin").equals("BTC")) {
                                    ArrayList<String> nameserversArr = new ArrayList<>();
                                    ArrayList<String> addressesArr = new ArrayList<>();
                                    coin = dataObj.getString("coin");
                                    name = dataObj.getString("name");
                                    url = dataObj.getString("url");
                                    category = dataObj.getString("category");
                                    subcategory = dataObj.getString("subcategory");
                                    description = dataObj.getString("description");
                                    reporter = dataObj.getString("reporter");

                                    if (dataObj.has("ip")) {
                                        ip = dataObj.getString("ip");

                                    } else {
                                        ip = "no ip";
                                    }

                                    if (dataObj.has("nameservers")) {
                                        nameservers = dataObj.getJSONArray("nameservers");
                                    }

                                    if (dataObj.has("addresses")) {
                                        addresses = dataObj.getJSONArray("addresses");


                                    }

                                    if (nameservers != null) {

                                        for (int j = 0; j < nameservers.length(); j++) {
                                            nameserversArr.add(nameservers.getString(j));
                                        }
                                    }

                                    if (addresses != null) {

                                        for (int j = 0; j < addresses.length(); j++) {
                                            addressesArr.add(addresses.getString(j).replaceAll("\\s+",""));
                                        }
                                    }
                                    String BITCOIN_ADDR = "Bitcoin address:";
                                    if (description.contains(BITCOIN_ADDR)){
                                        String descAddr = description.substring(description.indexOf(BITCOIN_ADDR)+BITCOIN_ADDR.length());
                                        Log.d("description",descAddr);
                                        addressesArr.add(descAddr);
                                    }
                                    status = dataObj.getString("status");
                                    for (int j = 0; j < addressesArr.size(); j++) {

                                        ScamObject scamObject = new ScamObject(id, name, url, coin, category, subcategory,
                                                description, reporter, ip, nameserversArr, status);
                                        String cleanAddr = addressesArr.get(j).replaceAll("\\s+","");

                                        hashMapObjects.put(cleanAddr, scamObject);
                                    }
                                }
                            }

                            String json = gson.toJson(hashMapObjects);

                            StringBuilder sb = new StringBuilder();
                            sb.append(json.replaceAll("addresses","data"));
                            savetofile(sb.toString());
                            Log.d("JSONRES: ", sb.toString());
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {

                    @Override
                    public void onErrorResponse(VolleyError error) {

                        stringRequest();

                    }
                });

        queue.add(jsonObjectRequest);
    }
    private void stringRequest(){

        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {

                        String idContect[] = response.split("id");
                        StringBuilder sb = new StringBuilder();
                        for (String anIdContect : idContect) {
                            if (anIdContect.contains("BTC") && !anIdContect.contains("ETH")) {
                                sb.append(anIdContect);
                            }
                        }
                        savetofile(sb.toString());
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Toast.makeText(MainActivity.this, "Try somthing else", Toast.LENGTH_SHORT).show();
            }
        });
        queue.add(stringRequest);

    }

}
