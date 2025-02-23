0 ： 自动目录
obsidian插件开发
1 这个是obsidian的插件官方示例文档，实现了一个小功能，Run npm run dev to compile your plugin from main.ts to main.js， 然后main.js在obsidian的插件目录下，然后obsidian会自动加载插件。 
项目名称帮我改成pytest
2 api.py是一个python脚本 
3 child_process存了可能的使用方法,在插件代码中，可以通过 child_process.exec() 来执行 Python 脚本，并获取执行结果。
4 现在我想要一个插件来测试一下调用这个py脚本
---
这是一个obsidian的插件开发矿建，功能都已实现，现在需要改一些东西
1 名字修改成 ”Heading_Create_Pages“ , cmd shift p 插件启动时也是这个名字
2 启动后2个参数名字 ， 参数1：Full_Path_Name,下面注释 完整路径及名字(文件夹a/b) , 参数2：Heading_levels，下面注释 向下拆解的层级（比如文章中有二级标题和三级标题， 参数2说明拆解这两层）