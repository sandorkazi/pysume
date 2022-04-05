# A Resume generator in Python

A Python based resume generator from YAML to HTML... I just got bored of managing LaTeX and/or docx...

Print it to pdf if you want to... do replace my work history though. ;)

Running `tox` in the project root generates all supported formats of the Resume in the output folder. Based on the
things specified in the input folder.

Sidenote: I was contemplating naming this OpenCV but that was already taken... :D

# Usage

1. Replace or add your profile picture to the `input` folder.
2. Edit `input/config.yml` according to your Resume.

In the project root folder run `tox` or `python -m pysume.resume input output`. Former requires you to install `tox`.

# References

Used the CSS from the HTML CV template of [Thomas Hardy](http://www.thomashardy.me.uk/).

