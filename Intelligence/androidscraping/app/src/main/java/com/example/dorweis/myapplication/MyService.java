package com.example.dorweis.myapplication;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.support.annotation.Nullable;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class MyService extends Service {

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String url = intent.getStringExtra(MainActivity.ADDRESS);
        getHTML(url);

        return START_NOT_STICKY;
    }

    private void getHTML(final String url){

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL link = new URL(url);
                    HttpURLConnection connection = (HttpURLConnection) link.openConnection();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    String result;
                    StringBuilder sb = new StringBuilder();
                    while((result = reader.readLine()) != null){
                        sb.append(result);
                    }
                    Log.d("TAG", sb.toString());
                    Log.d("TAG", "getHTML() before");
                    Intent intent = new Intent();
                    intent.setAction("maayan");
                    intent.putExtra("info", sb.toString());

                    Log.d("TAG", "getHTML() after");
                } catch (MalformedURLException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
