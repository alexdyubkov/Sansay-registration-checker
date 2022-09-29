'''
Purpose of the script:
This script checks the number of registration on Sansays(voip SanSBC devices) hosts based on Selenium module(same way usual users do it with a browser). 
'''


#############################import#########################################
import socket
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import sys
import requests
import json
from loguru import logger
############################################################################


#############################input##########################################
# on which sansay hosts we need to check a registration number
hosts = ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx']
port = xxxx #example 8888
login = 'xxx' #this user must exist on Sansay
password = 'xxx'
# slack webhook url
url = "https://hooks.slack.com/services/..."


names = {  # names for sansays, if you want to add more hosts, please follow the same format. Helps to transform ip to names
    #'sansay_name': :https://ip:port/SSConfig/User/control'
    'xxx1': 'https://ip:port/SSConfig/User/control',
    'xxx2': 'https://ip:port/SSConfig/User/control',
    'xxx3': 'https://ip:port/SSConfig/User/control'
}

triggers = { # triggers for sansays registration numbers
    #'sansay name':trigger_number
    'xxx1': 666,
    'xxx2': 666,
    'xxx3': 666}  

#chosen time range
start = '07:59'  # if we are inside this time range the script will be triggered -> it'll send to slack no matter what results
# are.
# If we are out of the range -> it will trigger only if it's trigger
# limits for sansay registration numbers
end = '15:01'
############################################################################


#############################logic##########################################
@logger.catch
def main():
    def logs():
        logger.add('sansay_reg_checker_log', format="{time} {level} {message}", level='INFO', rotation='10 KB', retention="90 days")

    

    logs()
    logger.info("Starting script....")

    def input_checker():
        if (len(names) != len(hosts)) or (len(names) != len(triggers)):
            logger.error("\n\nThe number of hosts is not equal to the number names, please give names to all hosts\n\n")
            exit()


    input_checker()

    def check_connection_to_hosts(hosts: list, port: int) -> list:
        result_of_function = []
        logger.info(f"checking_connection_to_hosts by ip and port...: ")


        for i in hosts:
            a_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)  # tcp ipv4 socket
            a_socket.settimeout(10)    
            a_socket_with_ip_port = a_socket.connect_ex((i, port))

            if a_socket_with_ip_port == 0:
                #print(f'{i}:{port} is open')
                result_of_function.append(f'{i}:{port} is open')
                a_socket.close()
            else:
                #print(f'{i}:{port} is closed')
                result_of_function.append(f'{i}:{port} is closed')
                a_socket.close()
        # returns like ['xxx.xxx.xxx.xxx:8888 is open', 'xxx.xxx.xxx.xxx:8888 is
        # open', 'xxx.xxx.xxx.xxx:8888 is closed']
        logger.info(f"connection to hosts by ip and port result: "+ str(result_of_function))
        return(result_of_function)

    check_connection_to_hosts_result = check_connection_to_hosts(hosts, port)


    def show_only_reachable_sansays() -> list:
        list_of_reachable_sansay_hosts = []
        # filter only reachable sansay hosts from all input sansays. Result
        # ['xxx.xxx.xxx.xxx:port is open', 'xxx.xxx.xxx.xxx:port is open']
        for i in check_connection_to_hosts_result:
            if 'open' in i:
                list_of_reachable_sansay_hosts.append(i)

        list_of_reachable_sansay_hosts_only_ip_and_port = []  # show only ip+port
        for i in list_of_reachable_sansay_hosts:
            list_of_reachable_sansay_hosts_only_ip_and_port.append(i.split(' ')[0])
        # returns like ['xxx.xxx.xxx.xxx:port', 'xxx.xxx.xxx.xxx:port',
        # 'xxx.xxx.xxx.xxx:port']
        return(list_of_reachable_sansay_hosts_only_ip_and_port)


    def registration_check_on_reachable_sansays() -> list:
        connection_link = []  # full links for reachable sansays
        for i in show_only_reachable_sansays():
            connection_link.append('https://' + i + '/SSConfig/User/control')
        # result like
        # ['https://xxx.xxx.xxx.xxx:port/SSConfig/User/control',
        # 'https://xxx.xxx.xxx.xxx:port/SSConfig/User/control',
        # 'https://xxx.xxx.xxx.xxx:port/SSConfig/User/control']

        options = webdriver.ChromeOptions()  # preconfigure chrome driver
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(options=options)

        num_of_registered_users = []
        for i in connection_link:
            browser.get(i)  # open each sansay link

            input_login = browser.find_element_by_xpath(
                "//input[@name='j_username']")  # log in
            input_password = browser.find_element_by_xpath(
                "//input[@name='j_password']")
            login_button = browser.find_element_by_xpath("//input[@value='login']")
            input_login.send_keys(login)
            input_password.send_keys(password)
            login_button.click()

            subscriber_stats_tab = browser.find_element_by_xpath(
                "//*[@id='tabbar2']/ul/li/a[contains(text(),'Subscriber Stats')]")  # open subs tab
            subscriber_stats_tab.click()

            num_of_registered = WebDriverWait(browser, 10).until(  # grep number of registration
                EC.visibility_of_element_located((By.XPATH, "//font[@id='numSubs']")))
            num_of_registered = num_of_registered.get_attribute('innerHTML')
            num_of_registered_users.append(i + ': ' + str(num_of_registered))
        browser.quit()
        # print(num_of_registered_users)
        # returns like ['https:/xxx.xxx.xxx.xxx:port/SSConfig/User/control: №ofregistraitions',
        # 'https://xxx.xxx.xxx.xxx:port/SSConfig/User/control: №ofregistraitions',
        # 'https://xxx.xxx.xxx.xxx:port/SSConfig/User/control: №ofregistraitions']
        return num_of_registered_users


    def link_to_name_converter() -> list: # converts ['https://xxx.xxx.xxx.xxx:port/SSConfig/User/control: №ofregistrations'] -> ['sansay_name: №ofregistrations']
        result = []
        for i in registration_check_on_reachable_sansays():
            k = i.split(': ')[0]
            for value in names.values():
                if k == value:
                    # Key from Python Dictionary using Value
                    key = str({y for y in names if names[y] == k})
                    key = key[2:-2]
                    result.append(str(key) + ':' + str(i.split(': ')[1]))
        # returns like ['sansay_name: №ofregistrations', 'sansay_name: №ofregistrations']
        logger.info(f"for reachable hosts the registraion level is: " + str(result))
        return(result)
    result_of_link_to_name_converter=link_to_name_converter()


    def is_hour_between(start: str, end: str, now=None) -> bool:
        now = datetime.now().strftime('%H:%M:%S.%f')[:-10]  
        is_between = False

        if (now > start) and (now < end):
            is_between = True
        else:
            is_between = False
        logger.info("Are we inside the chosen time range? " + str(is_between))
        return is_between  # returns True if we are inside the range you chose


    def connection_issus_to_at_least_one_host() -> bool:
        result = False
        for i in check_connection_to_hosts_result:
            if 'closed' in i:
                result = True
        return result  # returns True => connection issue exists, False => no issues


    def registration_trigger_issue() -> str:
        result = ''
        for i in result_of_link_to_name_converter:  
            link_to_name_converter_key = i.split(':')[0]  
            link_to_name_converter_value = i.split(':')[1]  

            triggers_value = (triggers[link_to_name_converter_key])

            if int(triggers_value) <= int(link_to_name_converter_value):
                result += '  '
                result += i
        
        if result == '':
            logger.info('hit the registration trigger limit: No')  
        else:
            logger.info('hit the registration trigger limit: Yes' + result)

        return result  # returns '' if didn't hit the trigger, retuns  'sansay_name:№ofregistrations' if we hit the trigger    
    result_registration_trigger_issue=registration_trigger_issue()

    def sender(color, title, message):
        slack_data = {
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": title,
                            "value": message,
                            "short": "false",
                        }
                    ]
                }
            ]
        }
        byte_length = str(sys.getsizeof(slack_data))
        headers = {
            'Content-Type': "application/json",
            'Content-Length': byte_length}
        response = requests.post(url, data=json.dumps(slack_data), headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)


    def send_to_slack_conditions():  # send to slack based on conditions
        if is_hour_between(
                start,
                end):  # if we are in chosen hour =>send to slack no matter what

            # connection failed to at least 1 host=red message, otherwise violet
            # message
            for i in check_connection_to_hosts_result:
                if 'closed' in i:
                    message = ('Connection status to Unite Sansays: ' +
                            '\n' +
                            str(check_connection_to_hosts_result) +
                            '\n\n' +
                            'Registration count is:  ' +
                            '\n' +
                            str(result_of_link_to_name_converter))
                    title = (f"Unite Sansay registration :scream_cat:")
                    color = "#ee3333"
                else:
                    message = ('Connection status to Unite Sansays: ' +
                            '\n' +
                            str(check_connection_to_hosts_result) +
                            '\n\n' +
                            'Registration count is:  ' +
                            '\n' +
                            str(result_of_link_to_name_converter))
                    title = (f"Unite Sansay registration :pika:")
                    color = "#9733EE"
            sender(color, title, message)

        else:  # we are not in chosen hours
            if connection_issus_to_at_least_one_host():  # can't connectn to at least 1host
                message = ('Connection status to Unite Sansays: ' +
                        '\n' +
                        str(check_connection_to_hosts_result) +
                        '\n\n' +
                        'Registration count is:  ' +
                        '\n' +
                        str(result_of_link_to_name_converter))
                title = (f"Unite Sansay registration :scream_cat:")
                color = "#ee3333"
                sender(color, title, message)

            elif result_registration_trigger_issue != '':  # hit at least 1 trigger
                message = ('One of sansays hit the registration trigger!: ' +
                        '\n' +
                        result_registration_trigger_issue +
                        '\n\n' +
                        'Connection status to Unite Sansays: ' +
                        '\n' +
                        str(check_connection_to_hosts_result) +
                        '\n\n' +
                        'Registration count is:  ' +
                        '\n' +
                        str(result_of_link_to_name_converter) +
                        '\n')     
                title = (f"Unite Sansay registration :scream_cat:")
                color = "#ee3333"
                sender(color, title, message)

    try:
        send_to_slack_conditions()
        logger.info("Sended to slack: no errors")
    except Exception as e:
        logger.info("Sended to slack:  exception occured")
        logger.error(e)

    #Login of send_to_slack_conditions():
    #1)Are we between chosen time range? -> yes -> 2)post to slack the results you get
    #                                    -> no  -> 2)connection to all hosts is good? -> no -> 3)post to slack the results you get
    #                                                                                 ->yes->  3)did we hit the trigger? -> no -> 4)end of the programm
    #                                                                                                                       yes-> 4)post to slack the results you get

    logger.info("Ending script....")

if __name__ == "__main__":
    main()
############################################################################
