package com.example.dorweis.myapplication;

import java.util.ArrayList;

public class ScamObject {
    int id = 1;
    String name = null;
    String url = null;
    String coin = null;
    String category = null;
    String subcategory = null;
    String description = null;
    String reporter = null;
    String ip = null;
    ArrayList<String> nameservers = new ArrayList<>();
    String addresses = null;
    String status = null;
    public ScamObject(int id, String name, String url, String coin, String category, String addressesArr, String subcategory, String description, String reporter, ArrayList<String> nameservers, String status) {
        this.id = id;
        this.name = name;
        this.url = url;
        this.coin = coin;
        this.category = category;
        this.subcategory = subcategory;
        this.description = description;
        this.reporter = reporter;
        this.ip = ip;
        this.addresses = addressesArr;
        this.nameservers = nameservers;
        this.status = status;
    }

    public int getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getUrl() {
        return url;
    }

    public String getCoin() {
        return coin;
    }

    public String getCategory() {
        return category;
    }

    public String getSubcategory() {
        return subcategory;
    }

    public String getDescription() {
        return description;
    }

    public String getReporter() {
        return reporter;
    }

    public String getIp() {
        return ip;
    }

    public ArrayList<String> getNameservers() {
        return nameservers;
    }

    public String getStatus() {
        return status;
    }
}
