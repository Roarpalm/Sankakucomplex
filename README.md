### all id.txt:
用以保存已爬取的id，避免重复爬取

### all href.txt:
用以保存已解析的url

### fail_sankaku.txt:
用以保存下载失败的url，建议手动复制进浏览器打开

### bad id.txt:
用以保存解析失败的id

### id.txt:
用以保存当前任务爬取的id

### href.txt:
用以保存当前任务解析的url

### sankaku_no_error.py:
核心代码

### 第一步：获取id.py:
爬取id

### 第二步：获取href.py:
通过id解析url

### 第三步：下载.py:
下载

- - - -

### 2020年4月1日更新(1.1):
- 新增 ```file_type()``` 函数，对下载后的文件进行分类
- 新增 ```run_main()``` 函数，捕获连接失败异常并在异常后恢复 ```id.txt```

### 2020年4月2日更新(1.2):
- 新增 ```rewrite()``` 函数，用以恢复 ```id.txt```
- 删除 ```file_type()``` 函数
- ```get_href()``` 函数新增解析失败重新解析功能
- ```download``` 函数实现文件分类
- 修改部分文字表述

### 2020年4月3日更新(2.0):
- 这家网站有点小气，我只开5个协程去请求，每次请求完等待5秒，就这样他还是频繁给我报 ```HTTP:429 too many requests - please slow down...```
- 但还算友好，毕竟是429，不是直接封我ip
- 全新改版 2.0
- 新增 ```sankaku_no_error.py``` ，核心代码，无任何纠错，因网站限制和网络波动基本不可能运行完成，仅供展示
- 将原本一个程序拆分为三步，需手动依次执行
- 原因在于网络不稳定性，某些时段请求网页经常连接超时，分三步更可控，减少不必要的重复执行
- 三步代码里都加入了大量试错，较为臃肿
- 删除exe文件夹，待以后整合优化再补上

### 2020年4月3日更新(2.1):
- 新增 ```GUI.py```，赋予 ```第一步：获取id.py``` 一个简单的图形界面

### 2020年4月6日更新(2.2):
- 将 ```第二步：获取href.py``` 中的整体读写改成异步读写
- ```get_href()``` 函数会在解析url的同时对 ```all href.txt```、```href.txt```、```id.txt``` 做同步修改，即使中途出错中断也可以随时再次运行第二步直到解析完所有id
- ```第三步：下载.py``` 将不再下载超过20M的文件，那些多半是从小电影截取的片段，不好看还浪费时间
- 学会把 ```\\``` 换成 ```os.sep``` ，mac和win不用自己改了

### 2020年4月8日更新(2.3):
- ```第三步：下载.py``` 加入对 ```href.txt``` 的实时修改，反复运行更顺畅