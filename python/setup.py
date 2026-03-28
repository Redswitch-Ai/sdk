from setuptools import setup, find_packages

setup(
    name="redswitch",
    version="1.0.0",
    description="The failsafe for autonomous AI agents",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    author="RedSwitch",
    author_email="protocol@redswitch.ai",
    url="https://github.com/Redswitch-Ai/sdk",
    py_modules=["redswitch"],
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai agent lifecycle monitoring heartbeat failsafe",
)
