## command


<--! docker-compose run --rm =>> will remove the docker container after ran the command.(onetime-command) so that docker container will not fill-up
docker-compose run -rm app sh -c "python manage.py <your required keyword>"  
docker-compose run app sh -c "django-admin startproject app ."
docker-compose run app sh -c "python manage.py test"

# ekokart-app-api
Ekokart app api source code

## Creating Dockerfile
    1) Select the Simgple tags for docker ()https://hub.docker.com/_/python)
    2) create 'Dockerfile' undre root projocet folder
        i) mention version of python that will be going to run
        ii) who will be maintainer
        iii) copy requirements.txt from root project folder (./) to docker container
        iv) run pip command to install application from requirements.txt
        v) run command 'mkdir /app' to create folder 'app' before current path (./)
        vi) WORKDIR => it will create /app/ folder as working directory 
        vii) copying root folder's /app/ directory to Docker container's /app/
        viii) RUN adduser will make 
            ==>> basically says 'add user' which creates a user.
                the '-D' says create a 'user' that is going to be used for running applications only.
                Not for basically having a home directory and that someone will log in to 
                it's going to be used simply to run our processes from our project.
        ix) Finally 'USER' user switches Docker to the user that we'have jsut created.
      ### Note: The reason why we do this is for security purposes.
                If you don't do this then the image will run our application using the root account which is not recommended
                because that means if somebody compromises our application they then have roup access to the whole image
                and they can go do other than vicious things.
                whereas if you create a separate user just for our application then this kind of limits the scope that
                an attacker would have in our documentation.

## Creating UnitTest (test_model.py, test_admin.py
    ## You never want to depend on external services to be running when you write unit tests, as this would make your tests fragile and unpredicable
    ## It's never a good idea to make a test always pass, as this would defeat the purpose of helping you identify issues in your code
        
    1) best practice write TESTCase under seprate tests/test_<objects>.py 
    2) test_case class_name should end with '<clas_name>Tests(TestCase):
    3) Test_Case method should start with 'test_<test__Case_name>
        i) where we run 'python manage.py test' Django searches for any Python Module starting with "test"
        ii) method 'def setUp(self):' function will run before every Test in Test CAses
        
    4) each test in user/test/test_user_api.py it will create clean and create new database so information from 1 test_case wont pass to others
    

## Mocking with Unittest (test_Command.py)
    1) Mocking is used to isolate the specific code to be tested and to avoid unintended consequences of running your unit tests
    2)Mocking is used when you actually don't want to have final perform but still wants to check is piece of code is working
        by mocking.
        eg; testing with sending email. instead of sending email will intercept in middle using mocking as verify parameters
    
    
    2) creating wait_for_db.py for test_command.py
        i) django recommended to put all 'commands; in directory called 'management' and the forward slash
        ii) 
  
## creating 'user' app =>> docker-compose run --rm app sh -c "python manage.py startapp user"
    1) we are removing admin, app, models.py because we will use from 'core' app
    2) we are removing tests.py because we will add 'test' directory for unittest
    
## creating Token authentication 
    1) The benefit of this is you don't need to send the user's username and password with every single request that you make.
            You just need to send it once to create the token and then you can use that token for future requests
             and if you ever want to revoke the token you can do that in the database.
    2) We're going to start by creating 4 unit tests. 'Test_user_api.py'
           i) we're going to create one unit test that tests that the token is created okay.
           ii) we're going to create another unit test that checks what happens if we provide invalid credentials.
            iii) Then we're going to create another one that checks if you're trying to authenticate against a non-existent user.
            iv) And finally we're going create the fourth one which is if you provide a request that doesn't include a password.
    3) added TOKEN_URL = reverse('user:token') =>>>> test_user_api.py
    4)   
    