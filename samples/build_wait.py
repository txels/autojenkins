from autojenkins import Jenkins

j = Jenkins('http://jenkins.live')
result = j.build('mbf-order-dcs-us677_merge_dev_carles', wait=True)
print('Result = ' + result['result'])
