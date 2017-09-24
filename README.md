# whynot

This is a re-implementation of the matlab `why.m` module.


## install

TODO: more

```bash
pip install <url or path to this repo>
```


## usage

TODO: explain args

```bash
whynot [--config /path/to/config] [--seed <int>] [<entry_point>]
```

This is where the name of this package really shines. You want to use a custom
config? Just add `alias why='whynot -c /path/to/my/config` to your `.bashrc` or
equivalent!


## config

TODO: explain config

If you need to debug your config, you can see the parsed result of the config by
running:

```bash
python -m whynot.config [config]
```

TODO: explain config locations and environment variables
