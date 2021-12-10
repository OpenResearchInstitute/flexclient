# Python client module for FlexRadio 6K series radios

NOTE: This is a very early alpha release which is very fussy to use. It is not recommended for general use.

The FLEX-6000 series radios are software defined "radio Servers" with components and calibrations usually defined in hardware instead implemented with software.

The radio is used via a gigabit ethernet port, which allows users to send commands and open further connections to receive and transmit.

Fles Radio has released an open API, but it is restrictive due to the fact it is built with the .NET framework.
Building a new API enables cross-platform uses of the SDR, opening many more opportunities to use its potential.

The initial purpose of this module was to support gnuradio blocks which use the radio, but it can also be used to develop clients in pure python.

Contributing:

We use the black code formatter, and ask that all submissions be formatted with black before making a pull request.
