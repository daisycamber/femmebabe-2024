This is a full stack web app focused on data visualization, machine learning, computer vision, facial recognition, biometrics, security, payment processing, marketing, ease of use, and more.

To deploy, begin with an Ubuntu server connected to the internet and add an A record pointing to the server in the DNS configuration of the domain you want to use. Run the unix-setup script from my other repository (https://github.com/daisycamber/unix-setup) first, titled "initialize", and paste in your SSH key before you run it in the key here section. Then, clone and move the repository to a new directory with a memorable name within home. Create config/apis.json and config/config.json as well as config/etc_dovecot_passwd as per the example (-example) replacing PASSWORDHERE with a memorable password also in the config json, and update both json files with keys as per the settings.py. Make sure to update any neccesary settings in settings.py as well. Next, edit scripts/convert to denote new names for the domain, directory, project, and user. Cd to the directory and run scripts/convert with ./scripts/convert before running scripts/setup and allowing the software to install. Copy and paste the IP address, ipv6 address, domain key, and all other neccesary records into the DNS configuration. Lastly, add a reverse DNS (rDNS) record to your server with the domain name you are using through your hosting provider.

Online at https://femmebabe.com

I develop this software without compensation, so any support is appreciated! Please share this project with your friends, coworkers and community. You may also hire me, subscribe to my blog, an ID scanning plan, or custom services on my website above.

Thank you for visiting!
- Charlotte Harper