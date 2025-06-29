# Shell
#shell

是否与[6-a (Linux Tools)](6-a%20(Linux%20Tools).md)有重合情况？

[ShellCheck – shell script analysis tool](https://www.shellcheck.net/)
[shell 是如何知晓文件需要使用 sh 来解析的](https://en.wikipedia.org/wiki/Shebang_(Unix))

> [!Abstract] 目录
> 

## Shell 脚本
### Shell特殊字符

|  特殊字符   |      功能       |
| :-----: | :-----------: |
|   $0    |     脚本名称      |
| \$1-\$9 | 脚本参数，$1为第一个参数 |
|   $@    |     所有的参数     |
|   $#    |     参数数量      |
|   $?    |  上一条命令的执行返回值  |
|   \$$   |  现在这个脚本的PID   |
| !!<br>  |   完整的上一条命令    |
|   $_    | 上一条命令的最后一个参数  |
|         |               |

> [!info] Link
> [Special Characters (tldp.org)](https://tldp.org/LDP/abs/html/special-chars.html)
> [指令结果作为参数使用](files/slides/6.null/missing%20semester%20en.pdf#page=12&selection=65,0,126,1)

> [!Example]
> 
> 
> ```bash
>  #!/bin/bash 
>  echo "Starting program at $(date)" 
>  # Date will be substituted 
>  echo "Running program $0 with $# arguments with pid $$" 
>  	for file in "$@"; do 
>  		grep foobar "$file" > /dev/null 2> /dev/null 
>  		# When pattern is not found,grep has exit status 1 
>  		# We redirect STDOUT and STDERR to a null register
>  		# since we do not care 
>  		if [[ $? -ne 0 ]]; then 
>  			echo "File $file does not have any foobar" 
>  			echo "# foobar" >> "$file" 
>  		fi 
>  	done
> ```


### Shell中的字符串

Strings delimited with ' are literal strings and will not substitute variable values 
whereas " delimited strings will.
> [!Example]
> 
> 
> ```bash
> foo=bar 
> echo "$foo"
> # prints bar 
> echo '$foo'
> # prints $foo
> ```

### Shell脚本的可移植性

> [!example]
> ```bash
> # for specific opreating systems
> if [[ "$(uname)" == "Linux" ]]; then {do_something}; fi 
>
> # Check before using shell-specific features 
> if [[ "$SHELL" == "zsh" ]]; then {do_something}; fi 
>
> # You can also make it machine-specific 
> if [[ "$(hostname)" == "myServer" ]]; then {do_something}; fi
> ```
