***1)#####################General info:#########################***
<br>
Sansays are VoIP SBC. 

Sometimes there is no way to receive the subscriber's registrations information from CLI. This script imitates user's actions by using Selenium.

Scripts can be set via crontab. 

In script itself, you can pick the time range window. If scripts starts during this time range, it will send results to slack.
If you're out of the chosen time range, the script checks the connection to hosts and checks the registration triggers you manually set. In case something is wrong, it'll notify you in your slack.

Script creates logs in the folder of the script.


<!-- blank line -->
----

***2)#####################Script logic:#########################***<br>
```mermaid
graph TD;
    A[Start] --> B{1.Are we in chosen time range?}
    B -->|yes| C[2.Post to slack the results]
    B -->|no| D[2.Is there a connection with all hosts from the list?]
    D-->|yes| F[3.Did we hit the registration trigger?]
    D -->|no| E[3.Post to slack the results]
    F-->|yes| L[4.Post to slack the results]
    F-->|no| K[4.End of the script without posting to slack]
```
