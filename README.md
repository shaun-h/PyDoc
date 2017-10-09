# PyDoc
PyDoc is a docset browser written in python for [Pythonista](http://omz-software.com/pythonista/). 

## Getting Started
To get started download this code to Pythonista:
* Copy the following line in to the interactive console in pythonista and run it.

```python
import requests as r; exec(r.get('https://goo.gl/giwri9').text)

```

* Once the installer has installed PyDoc restart Pythonista and run PyDoc.py in the PyDoc folder and this will start the application.

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

Docsets are provided by Dash the MacOS docset browser. Please checkout Dash please by clicking the link below.

[Dash](https://kapeli.com/dash)

## Updates

Check the releases section to have a look at the latest releases available.

## Road Map

- Docset update functionality
- Transfer functionality
- Live updating for theme change (no restart required)

## Known Issues

- Implement better error handling currently all errors are treated like they are fatal
