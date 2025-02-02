# How to Run the ProjectPlanner Application

For running this small application, you need a device (laptop), virtual machine, or container that has a running installation of **Python** (code was developed on Python 3.11.2) and a **PostgreSQL server** installation.

## Steps to Set Up and Run the Application

1. **Clone the repository** by opening your terminal in your preferred IDE (new project) or by executing the following command in bash in the folder of your choosing:

   ```bash
   git clone -b main https://github.com/elabbk/application-projectplanner
   ```
   
2. **Initiate the PostgreSQL server** by opening the `psql` shell. You will be prompted to assign the following attributes. Press **Enter** to select the default values in brackets or set your own value. Note down the values you set.

   ```shell
   Server [localhost]:
   Database [postgres]:
   Port [5432]:
   Username [postgres]:
   Passwort für Benutzer postgres:
   ```

3. **Create a file .env** by using .env.sample.devcontainer as an example with the above parameters for PostgreSQL

4. **Install the required dependencies** by opening the terminal in your IDE or executing the following command in bash:

   ```bash
   cd application-projectplanner
   pip install -r requirements.txt
   ```

4. **Run the application** by executing the following command in the terminal:

   ```bash
   flask run
   ```
   
The project is based on a sample application. Contributions from other authors that are not mine can be seen in the git history. 

