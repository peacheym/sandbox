# Trill Mapper

## libmapper Installation

Ensure that you have installed libmapper on your Bela board. If you have not yet installed libmapper, follow the guide provided in the [github repo](https://github.com/libmapper/libmapper).

## Make Parameters

You will need to include the following make parameters.

```
LDFLAGS=-L/usr/local/lib; CPPFLAGS=-I/root/liblo/include -I/root/libmapper/include;LDLIBS=-lmapper -llo;
```
