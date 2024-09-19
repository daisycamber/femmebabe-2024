This is a full stack web app focused on data visualization, machine learning, computer vision, facial recognition, biometrics, security, payment processing, marketing, ease of use, and more.

To deploy, begin with an Ubuntu server connected to the internet and add an A record pointing to the server in the DNS configuration of the domain you want to use. Run the unix-setup script from my other repository (https://github.com/daisycamber/unix-setup) first, titled "initialize", and paste in your SSH key before you run it in the key here section. Then, clone and move the repository to a new directory with a memorable name within home. Create config/apis.json and config/config.json as well as config/etc_dovecot_passwd as per the example (-example) replacing PASSWORDHERE with a memorable password also in the config json, and update both json files with keys as per the settings.py. 
Generate API keys for Google recaptcha, maps, NowPayments (use my link - https://account.nowpayments.io/create-account?link_id=3423046394&utm_source=affiliate_lk&utm_medium=referral ) and all other desired APIs.
Make sure to update any neccesary settings in settings.py as well. Next, edit scripts/convert to denote new names for the domain, directory, project, and user. Cd to the directory and run scripts/convert with ./scripts/convert before running scripts/setup and allowing the software to install. Copy and paste the IP address, ipv6 address, domain key, and all other neccesary records into the DNS configuration. Lastly, add a reverse DNS (rDNS) record to your server with the domain name you are using through your hosting provider.

Online at https://lotteh.com

I develop this software without compensation, so any support is appreciated! Please share this project with your friends, coworkers and community. You may also hire me, subscribe to my blog, an ID scanning plan, or custom services on my website above.

Sample DNS configuration:
;; QUESTION SECTION:
;lotteh.com.			IN	TXT

;; ANSWER SECTION:
lotteh.com.		1799	IN	TXT	"v=BIMI1;l=https://lotteh.com/media/static/lotteh.svg"
lotteh.com.		1799	IN	TXT	"v=spf1 mx ip4:75.147.182.214 ip6:2601:602:8901:3914:725a:fff:fe49:3e02 ~all"

;; QUESTION SECTION:
;sendonly._domainkey.lotteh.com.	IN	TXT

;; ANSWER SECTION:
sendonly._domainkey.lotteh.com.	1796 IN	TXT	"v=DKIM1;h=sha256;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuD59wLd7aOqkO6u3lXt/eXVCoewxl4SbxXpGhhYzthxuNeDn9EHagSbLmMeYsF0gdY+fAEOtq26hdjvxGbe19ZEYOFP3tBYxXR8hYKE3F0fDQdwYR8aUvvXsImD0HmqvaDHrzjEjIn7EE6KLc++Gh6UC1KqVhyR7B3MfQSXo2y32g6HArxRCs+EdzF" "86yRQViLF+6uQNavoCkhFEI7TfqfwxV0gYFWjAs5NV/xoJiXeD457LsLiwM/uWfgVN7RIBNDxhuLBHAH4hvTtKXZdxol+ttMOtGbsbTaXH17ZrmfZd2bVswT3WR5eMRRtiX3M3r7+gQsuS0X2nxAdicfBpWwIDAQAB"

As well as A and AAAA record matching the SPF record above.

Thank you for visiting!
- Charlotte Harper