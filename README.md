## Opcua Server

### 简介

### 环境需求

- 安装python

- 安装scons

执行命令 `python -m pip install B:/boboli/rep/software/scons/scons-3.1.1-py2.py3-none-any.whl`

#### 安装vscode

window： 安装`B:\boboli\rep\software\vs_code\VSCodeUserSetup-x64-1.40.2.exe`

安装cpp插件：打开vscode，`ctrl+shelf+p`, 输入命令`install from vsix`，然后选中`B:\boboli\rep\software\vs_code\cpptools-win32.vsix`

工程配置：

- 将`B:\boboli\rep\software\vs_code\vscode_example`目录下的`.vscode`拷贝到工程目录下
- 修改`c_cpp_properties.json`文件里面的`"compilerPath"`将vs编译环境设置好
- 在termial中设置默认shell为`Command Prompt`即cmd
- `c_cpp_properties.json`为编译环境配置
- `launch.json`为debug环境配置，设置`"program"`启动调试的文件，按`F5`启动
- `tasks.json`为编译配置，按`ctrl+shelf+B`启动工程的编译，里面已有选择`build_ms`,`test_ms`和`clean`

工程配置好后，打开vscode->File->Open Folder->Choose Follder选中工程目录，即可编译调试

### 编译使用

在工程根目录终端下执行，常用命令如下：

编译: `scons`

清除编译文件:`scons -c`

编译debug版本:`scons debug=yes`

编译时添加宏定义:`scons define=Demo`

VS2017编译:`scons msvc=14.1`

VS2010编译:`scons msvc=10.0`

更多信息可通过`scons --help`查看
