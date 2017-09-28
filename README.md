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

- 1.3.1 - Added Dark Orange Theme
- 1.3 - Added themes

- 1.2.1 - Made some minor updater UI changes
- 1.2 - Added PyDoc update funtionality

- 1.1 - Added searching (this is both search across all docsets as well as individual)

- 1.0 - Initial Release

## Road Map

- Docset update functionality
- Transfer functionality
- Improved WebView
- Adding stackoverflow docsets
- Live updating for theme change (no restart required)

## Known Issues

- Implement better error handling currently all errors are treated like they are fatal
