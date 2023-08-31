# 如何贡献 OpenTenBase

## 贡献文档

1. Fork [文档仓库](https://github.com/bartdong/docs/fork)
2. 将您 Fork 后的文档仓库 clone 至本地

    ```
    git clone git@github.com:yourname/docs.git # (1)
    ```

    1.（你需要将 `yourname` 更换为你自己的 GitHub 用户名）

3. 安装环境
    - 安装 Python 3.x
    - 安装 [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 及多语言插件

    ```
    pip install mkdocs-material mkdocs-static-i18n
    ```

    - 在本地运行预览服务器

    ```
    mkdocs serve
    ```

4. 可以开始贡献啦！
    - 具体 markdown 及本文档站支持的显示特性可查看 mkdocs-material 的[说明文档](https://squidfunk.github.io/mkdocs-material/reference/)。
    - 请注意遵守本文档站的 [格式手册](docs-format-guide.md)。

5. 在本地通过预览服务器确认内容与格式正确后，commit 您的修改。
6. 向[文档仓库](https://github.com/OpenTenBase/opencloudos.github.io)提交 Pull Request，待维护者审核后即可合并。


## 为代码做出贡献
---
如果您有好的意见或建议，欢迎创建[Issues](https://github.com/OpenTenBase/OpenTenBase/issues)或[Pull Requests](https://github.com/OpenTenBase/OpenTenBase/pulls)，为 OpenTenBase 开源社区做出贡献。OpenTenBase 不断招募贡献者，哪怕是回答 issue 中的问题，或者做一些简单的 bug 修复，都会对 OpenTenBase 有很大的帮助。
[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者参与和贡献，期待您的加入。

### Issue

#### 对于贡献者

提交问题前请确保满足以下条件：

* 必须是错误或新功能
* 已在 issue 中搜索过，没有找到类似的问题或解决方案
* 创建新问题时，请提供详细描述、截图或短视频，以帮助我们定位问题

### Pull Request

我们欢迎大家贡献代码，让我们的产品更加强大。代码团队会监控所有的 Pull Request ，我们会做相应的代码检查和测试。测试通过后，我们会接受 PR ，但不会立即合并到 master 分支。
完成 PR 前请确认：

1. 从 master 分支分叉出你自己的分支。
2. 修改代码后请修改相应的文档和注释。
3. 请在新创建的文件中添加许可证和版权声明。
4. 保证代码风格一致。
5. 进行充分的测试。
6. 然后，您可以将代码提交到dev分支。