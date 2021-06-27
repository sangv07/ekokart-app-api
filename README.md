## command
docker build .
docker-compose build

<--! docker-compose run --rm =>> will remove the docker container after ran the command.(onetime-command) so that docker container will not fill-up
docker-compose run --rm app sh -c "python manage.py <your required keyword>"  
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
     """
     When writing software it's important to include unit tests with your code unit tests are simply tests 
        which check that your code does what it's supposed to do. You start by isolating the particular piece of code to be tested. This could be a function or a class.
        In our case most of the test we write will be making actual API calls to our endpoints. Knowing which code to target comes with practice.
        So this should become clearer by the end of the course. Tests are typically broken down into three stages. The first stage is the setup.
        This is where you would normally create some sample objects in your database that you can use to test your code.
        For example if we were testing an API endpoint that updates a recipe we would start by creating a sample
        recipe that we can use to test our endpoint. The second stage is the execution. This is where you actually call the code being tested.
        So in our example we would call our recipe update endpoint with our test client with the ID of the sample recipe and some sample fields to update.
        Then the final stage is the assertion stage where you check for the code performed what it was supposed to do.
        So in our recipe example we would ensure that the appropriate fields on our sample recipe were updated to the correct values
        If it doesn't fully make sense just yet don't worry it should become clearer as we work through the
        hands on examples in this course. So you might be thinking why go through all this effort of adding unit tests to our code.
        Well there are many benefits of writing unit tests which is why most professional development teams have a policy that they must be written for all code.
        The number one benefit of writing unit tests is it makes it a lot easier to maintain and make changes to your code. When you're making changes to code that has great test coverage
        you can be confident that if something breaks as a side effect of your change you will know about it when the tests run.
        This way you can identify and fix issues before they end up in the production build.
        It may take more time at first but in the long run it will actually save you time because adding features
        and making changes becomes a lot easier with the added confidence that tests bring. Another great benefit to writing unit tests
        is that it encourage developers to write testable code. In order for code to be testable there must be a clear input and output for each unit of code.
        This also happens to be what makes easy to read reliable code. So testable code = quality code. So what about test driven development or TDD.
        The classic way to write unit tests is you write the piece of code and then you write the unit tests With test driven development
        all you do is you switch this round so you start by writing the unit test then you ensure the test fails and then you implement the code or feature to make the test pass.
        So what's the benefit of doing it this way?
        Well firstly it increases test coverage because you can be sure that all code written with TDD has been tested. On top of this
        it helps ensure that your tests actually work. Just as there can be bugs in regular code there can also be bugs in test code.
        It's possible that if there's a mistake in your test that it will always pass whether your code is working
        or not. Test driven development helps avoid this because you check that the test fails before and passes after you implement the feature. Test driven development
        also encourages you to naturally write good quality code since bad code is often difficult to test. 
        Lastly the unit tests serve as a guideline for when to stop coding.
     """


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
    