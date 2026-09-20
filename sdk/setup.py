from setuptools import setup, find_packages

setup(
    name="ai-guardian",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["httpx>=0.27.0"],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "langchain": ["langchain>=0.1.0", "langchain-openai>=0.1.0"],
    },
)