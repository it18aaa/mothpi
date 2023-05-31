# mothpi

##Thoughts

-Recording at 48kHz
-start at 5am throught to 8am
-then 5pm through to 8pm

-Should be able to stream live audio whilst recording - how to do this?  recorded audio gets chucked into a array buffer then written out to disk after 48000 * num of seconds.
How to compress and stream on the fly?  

-What type of network? Static IP, do we have power to assign hostname, or do the raspberry pis need to report their address to somewhere - dynamic dns eg?

-What type of interface is wanted?   restful api, builtin http server, or vanilla ssh ?

-What size chunks for recorded wavs?

-Recorded wavs to stay on device or pushed to a central repository?

-How to monitor time sync / ntp?


