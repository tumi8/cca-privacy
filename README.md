# Push Away Your Privacy: Precise User Tracking Based on TLS Client Certificate Authentication

This repository contains additional information, measurement data, and tools for the paper *Push Away Your Privacy: Precise User Tracking Based on TLS Client Certificate Authentication* published at [TMA 2017](http://tma.ifip.org/main-conference/).

If you have any questions, please do not refrain from contacting one of the authors:

* Matthias Wachs [lastname] @ net.in.tum.de
* Quiring Scheitle [lastname] @ net.in.tum.de [PGP Key](https://pgp.mit.edu/pks/lookup?op=vindex&search=0xC258219436005410)
* Georg Carle [lastname] @ net.in.tum.de

If you want to reproduce our work, you might find the [TMA'17 PhD School Lab](https://github.com/quirins/tma17-ripeatlas-lab-participants) helpful, which reproduces parts of this paper.

Please use OpenPGP to protect the communication!

## Capturing TLS client certificate authentication traffic

To analyze TLS client certificate authentication, we used tcpdump command to capture TLS Client Certificate packets on APNs ports 443, 5223, 2195 and 2196:

`tcpdump -n -i eth6 -s 0 'tcp[((tcp[12:1] & 0xf0) >> 2)+5:1] = 0x0b  and tcp[((tcp[12:1] & 0xf0) >> 2):1] = 0x16 and ( tcp dst port 443 or tcp dst port 5223 or tcp dst port 2195 or tcp dst port 2196)' -G 3600  -w tls-cca-%Y%m%d-%H%M.pcap`


## Captured TLS Handshakes 

### APNs handshakes

For further analysis, we provide captures APNs of handshakes for iOS, macOS, and iTunes on Windows before and after the fix provided by Apple. We have rewritten MAC and IP addresses for privacy in a documented process. Please contact us should you require non-rewritten copies.

#### iOS 10.2
[iOS 10.2 (vulnerable)](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/apns_ios_10.2.pcapng_rewritten.pcapng) -- 
[iOS 10.2.1-beta4 (fixed)](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/apns_ios_10.2.1.beta4.pcapng_rewritten.pcapng)  

#### macOS 10.12.x
[macOS 10.12.2 (vulnerable)](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/apns_macos_10.12.2.pcapng_rewritten.pcapng) -- 
[macOS 10.12.3-beta4 (fixed)](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/apns_macos_10.12.3.beta4.pcapng_rewritten.pcapng)  

#### iTunes 12.5.4.42
[iTunes 12.5.4.42 on Windows 10 (vulnerable)](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/apns_itunes_windows.pcapng_rewritten.pcapng)

More files and versions are available in the same directory.

### FCM and WNS handshakes

In addition to Apple's APNs, we analyzed authentication traffic of Google's FCM and Microsoft's WNS push notification services for certificate based client authentication.

#### Google FCM
Google's FCM uses port TLS over TCP ports 5228 to 5230:
[Google FCM Handshake PCAP](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/google_fcm_handshake.pcapng_rewritten.pcapng)  

#### Microsoft WNS
Microsoft's WNS uses TLS over TCP port 443:
[Microsoft WNS Handshake](https://github.com/tumi8/cca-privacy/blob/master/pcaps/rewritten/microsoft_wns_handshake.pcapng_rewritten.pcapng)  


## Parsing tcpdump network dumps

Our first step is to parse the captured .pcap files into a database. This and further steps are described under *parser*.


## Certificate Analyses

We analyze the outputs from the queries above using Jupyter Notebook.
Its input data and the notebook files are accessible under *analyses*.
Please note that we have anonymized data where adviseable, and provide the scripts we used to do so.

## User Study

The (anonymized) raw data and scripts for our tracking user study can be found under *userstudy*

## RIPE Atlas Measurements

The folder *ripe_atlas* contains subdirectories *dns* and *traceroute*.

### DNS

The *dns* subdirectory contains the scripts used to resolve APNs DNS names through Ripe Atlas and extract one random target IP address per observed /24 subnet. 
Details are listed unter *dns/dns.md*.  
The resulting artifacts are also stored in the *ripe-atlas-dns-responses.tar.bz2* file in the *dns* subdirectory.

### Traceroute 

In the *traceroute* subdirectory, you will find scripts to generate global and german measurements, alongside with the target list, the resulting measurement IDs, and the resulting artifacts.


