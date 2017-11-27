# -*- coding: utf-8 -*-

import re
import json
from wox import Wox, WoxAPI


class Alias(Wox):

    def store(self):
        with open('data.json', 'w') as file:
            file.write(json.dumps(self.data))

    def save(self, key, value):
        #因为这个函数是通过JsonRPC调用的，属于一个新的线程，需要重新加载json文件
        self.load()
        self.data[key] = value
        self.store()

    def handle(self, order):
        WoxAPI.change_query(order, True)

    def load(self):
        try:
            with open('data.json') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
            with open('data.json', 'w') as file:
                file.write(json.dumps(self.data))

    def fuzzyfinder(self, user_input, collection):
        suggestions = []
        pattern = '.*?'.join(user_input)
        regex = re.compile(pattern)
        for item in collection:
            match = regex.search(item)
            if match:
                suggestions.append((len(match.group()), match.start(), item))
        return [x for _, _, x in sorted(suggestions)]

    def query(self, query):
        self.load()
        results = []
        for alias in self.fuzzyfinder(query, self.data):
            results.append({
                "Title": alias,
                "SubTitle": self.data[alias],
                "IcoPath": "Images/alias.ico",
                "JsonRPCAction": {
                    "method": "handle",
                    "parameters": [self.data[alias]]
                }
            })
        if " " in query:
            key, value = query.split(" ", 1)
            if key == "set" and "=" in value:
                alias, order = value.split("=", 1)
                results = []
                results.append({
                    "Title": "消息：",
                    "SubTitle": "正在设置：{} -> {}".format(alias, order),
                    "IcoPath": "Images/app.ico",
                    "JsonRPCAction": {
                        "method": "save",
                        "parameters": [alias, order]
                    }
                })
        return results


if __name__ == "__main__":
    Alias()
