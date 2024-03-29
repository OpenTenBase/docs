# How to Contribute to OpenTenBase

## Contribute to the documentation

1. Fork [the documentation repository](https://github.com/OpenTenBase/docs)
2. Clone the forked documentation repository to your local machine

    ```
    git clone git@github.com:yourname/docs.git # (1)
    ```

    1. (You need to replace `yourname` with your own GitHub username)

3. Configure the environment
    - Install Python 3.x
    - Install [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) and multi language plugin

    ```
    pip install mkdocs-material mkdocs-static-i18n
    ```

    - Run the preview server locally

    ```
    mkdocs serve
    ```

4. Start contributing!
    - Refer to mkdocs-material's [documentation](https://squidfunk.github.io/mkdocs-material/reference/) for more details about markdown and the features supported by this documentation site.
    - Please follow the [format guide](docs-format-guide.en.md) of this documentation site.

5. Verify if the content and format are correct through the preview server, and then commit your changes.
6. Submit a Pull Request to [the documentation repository](https://github.com/OpenTenBase/docs), and it will be merged after being reviewed.


## Contribute to the Code
---
If you have good comments or suggestions, welcome to create [Issues](https://github.com/OpenTenBase/OpenTenBase/issues) or [Pull Requests](https://github.com/OpenTenBase/OpenTenBase/pulls)，contribute to the OpenTenBase open source community. OpenTenBase continues to recruit contributors, even if it is answering questions in the issue, or doing some simple bugfixes, it will be of great help to OpenTenBase.

[Tencent Open Source Incentive Program](https://opensource.tencent.com/contribution) Encourage developers to participate and contribute, and look forward to your joining.

### Issue  
#### For contributors 

Please ensure that the following conditions are met before submitting an issue:

* Must be a bug or new feature
* Have searched in the issue, and did not find a similar issue or solution
* When creating a new issue, please provide a detailed description, screenshot or short video to help us locate the problem

### Pull Request  
We welcome everyone to contribute code to make our product more powerful. The code team will monitor all pull requests, and we will do the corresponding code inspection and testing. After the test passes, we will accept the PR, but will not immediately merge into the master branch.

Please confirm before completing a PR:

1. Fork your own branch from the master branch.
2. Please modify the corresponding documents and comments after modifying the code.
3. Please add License and Copyright declarations in the newly created file.
4. Ensure a consistent code style.
5. Do adequate testing.
6. Then, you can submit your code to the dev branch.
