from setuptools import setup

with open("README.md","r") as f:
    long_description = f.read()

setup(
    name="mkdocs-panzoom-plugin",
    version="0.0.8",
        description="MkDocs Plugin to enable pan & zoom on images and mermaid diagrams",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords="mkdocs zoom pan plugin mermaid images",
        url="https://github.com/PLAYG0N/mkdocs-panzoom.git",
        author="PLAYG0N",
        author_email="playg0nofficial@gmail.com",
        license="MIT",
        python_requires=">=3.7",
        install_requires=["mkdocs>=1.0.4", "beautifulsoup4>=4.9.0"],
        # package_dir={"": "mkdocs_panzoom_plugin"},
        # package_data={"custom": ["*.css","*.js" ,"*LICENCE"]},
        include_package_data=True,
        classifiers=[
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
        packages=["mkdocs_panzoom_plugin"],
        entry_points={
            "mkdocs.plugins": [
                "panzoom=mkdocs_panzoom_plugin.plugin:PanZoomPlugin",
            ]
        },
)
