import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openflix", # Replace with your own username
    version="0.0.1",
    author="Matthieu Jacquemet",
    author_email="",
    description="WebTorrent based streaming website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/MatthieuJacquemet/openflix",
    packages=setuptools.find_packages(),
    install_requires=["pyutils", "pyutils","flask","flask_restful","flask_sqlalchemy"],
    package_dir={"","openflix"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Web Development :: Web Site",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)