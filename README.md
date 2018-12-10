# docato
DOCument lAbeling TOol - a simple web-based appearance-aware tool to label text documents for information extraction

## Usage

1. Install.
2. Configure structure of information to be labeled and extracted (short demo video https://drive.google.com/open?id=0B3kv5PmF80J3MV9LZzU2elVlakk).
3. Upload documents and label (short demo video https://drive.google.com/open?id=0B3kv5PmF80J3T2l5WVpvcE5zMXM).

Demo videos are in Russian, but the user interface is both in English and Russian. If you have any questions regarding installation or usage, please feel free to ask: I do not have enough free time to write a comprehensive documentation, but I'll be happy to help.


## Installation

1) Install `Docker` (https://docs.docker.com/) - it is a very convenient environment to run lightweight virtual machines (containers). It supports all major operating systems. Docato is distributed via Docker containers, which are available via Docker Hub (https://hub.docker.com/r/windj007/).
2) Install `docker-compose` (https://docs.docker.com/compose/install/#install-compose) - it is a simple utility to manage Docker containers with no extra actions.
3) Download docker-compose config file for Docato https://raw.githubusercontent.com/windj007/docato/master/docker-compose.yml
4) Create `logs`, `media` and `mysql` folders to store logs, uploaded files and mysql data. Insert their full paths into docker-compose.yml (field `volumes`).
5) Execute `docker-compose up` from the folder containing your `docker-compose.yml`. After that Docker will start downloading all the needed container images from `hub.docker.com` (they are stored there prebuilt, with all dependencies packaged).

After that you can log in to Docato using `admin` login and `adminpwd` password. The admin site is available on `http://<server>/admin`. Using that site you can change passwords and create more accounts.

## License

Docato is licensed under MIT License, so you are free to use it in any way you like.

## Citing

If you find this project interesting and/or using it for you academic research, please consider citing the following paper:
```
@inproceedings{suvorov2017active,
  title={Active Learning with Adaptive Density Weighted Sampling for Information Extraction from Scientific Papers},
  author={Suvorov, Roman and Shelmanov, Artem and Smirnov, Ivan},
  booktitle={Conference on Artificial Intelligence and Natural Language},
  pages={77--90},
  year={2017},
  organization={Springer}
}
```

## Contributing

Docato was developed when I was a research scientist at the Federal Research Institute "Computer Science and Control" of the Russian Academy of Sciences (FRC CSC RAS), and was participating in projects on information extraction (fact extraction, relation extraction) from texts.

How I work on other projects in other organization, so I do not actively develop Docato. However, it is still actively used in FRC CSC RAS and some other organizations, so it may be considered as relatively stable and ready.
