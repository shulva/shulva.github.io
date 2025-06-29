# Git
#git

> [!NOTE] What is Git
> [Git for Computer Scientists](https://eagain.net/articles/git-for-computer-scientists/)
> [Explain Git with D3](http://onlywei.github.io/explain-git-with-d3/)

> [!NOTE] Git Command
> [Git Command](files/slides/6.null/missing%20semester%20en.pdf#page=59&selection=39,0,39,26)
> [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)

> [!NOTE] Advanced Git
> [Resources](files/slides/6.null/missing%20semester%20en.pdf#page=60&selection=172,0,172,9)
> [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
> [How to Write a Git Commit Message](https://cbea.ms/git-commit/)

> [!example]
> ##### git stash
> ###### 当有人与我改动同一分支,合并会有冲突现象
> ```
> 1 git stash //把本地的改动暂存起来
> 2 git pull  //拉取远端分支（此时本地分支会回滚到上次commit的情况，新的改动都存在了stash中）
> 3 git stash pop // 将栈顶改动重新加回本地分支，就可以继续修改了，当然，如果改好了就是add,commit,push啥的。。
> ```