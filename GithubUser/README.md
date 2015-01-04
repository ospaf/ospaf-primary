# Ospaf GithubUser Documentation

## based on github openAPI, basic authentication

+ Get user list by using 'get_data_between_a_b.py'
 - Command: python get_data_between_a_b.py  100 9000
 - API Details: "https://api.github.com/users?since="+`gh_user_id`+"&page_size=100";
 - Output: save to `gh_user_id`.txt
+ Get 'login' from all the `gh_user_id`.txt by using 'generate_logins.py'
 - Command: python generate_logins.py > new_file
 - Output: new_file
+ Get user details by using 'get_user_data_from_conf.py'
 - Command: python get_user_data_from_conf.py new_file begin_at end_with
 - API Details: "https://api.github.com/users/"+`gh_user_id`
 - Output: save to lots of `gh_user_id`.txt

+ Get user details by distribute the task ! 'task_distribute.py'
 - Command: python task_distribute.py
 - simply, we can edit the configuration files in task_distribute.py

# Clean the downloaded users 'clean_thread.py'
 - Command: python clean_thread.py 0 > 0_to_50.new

# Send data to mongodb
 - Command: python upload_data.py
 - Explain: each user file is in  a single.txt which is bad design...
            Cause my ext3 inode issue which is a good lesson to me!

- - -
Copyright 2014 Ospaf Lab Software, Inc. Unless otherwise marked, this work is licensed under a [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/).
