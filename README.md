1)#####################General info:#########################
Sansays are VoIP SBC. 

Sometimes there is no way to receive the subscriber's registrations information from CLI. This script imitates user's actions by using Selenium.

Scripts can be set via crontab. 

In script itself, you can pick the time range window. If scripts starts during this time range, it will send results to slack.
If you're out of the chosen time range, the script checks the connection to hosts and checks the registration triggers you manually set. In case something is wrong, it'll notify you in your slack.

Script creates logs in the folder of the script.
###########################################################



2)#####################Script logic:#########################
    #1)Are we in chosen time range? -> yes -> 2)post to slack the results
    #                               -> no  -> 2)connection to all hosts is good? -> no -> 3)post to slack the results you got
    #                                                                            ->yes -> 3)did we hit the registration trigger? -> no -> 4)end
    #
##########################################################   
    
