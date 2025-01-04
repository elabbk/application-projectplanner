document.addEventListener('DOMContentLoaded', () => {
    // Check if a username is already set in localStorage
    const savedUsername = localStorage.getItem('username');
    if (savedUsername) {
        document.getElementById('usernameDisplay').textContent = `User: ${savedUsername}`;
        loadUserProjects(savedUsername);
    } else {
        // Show the username modal if no username is set
        const usernameModal = new bootstrap.Modal(document.getElementById('usernameModal'));
        usernameModal.show();

        document.getElementById('submitUsername').addEventListener('click', () => {
            const usernameInput = document.getElementById('usernameInput').value.trim();
            if (usernameInput) {
                document.getElementById('usernameDisplay').textContent = `User: ${usernameInput}`;
                localStorage.setItem('username', usernameInput);
                usernameModal.hide();
                loadUserProjects(usernameInput);
            } else {
                alert('Please enter a username');
            }
        });
    }

    // Reopen the username modal on click
    document.getElementById('usernameDisplay').addEventListener('click', () => {
        const usernameModal = new bootstrap.Modal(document.getElementById('usernameModal'));
        usernameModal.show();
    });

    // Handle logout
    document.getElementById('logoutButton').addEventListener('click', () => {
        localStorage.removeItem('username');
        location.reload();
    });

    // Handle Overview click to reload the overview page
    document.getElementById('overview').addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/overview';
    });

    // Function to load user projects
    function loadUserProjects(user) {
        fetch(`/api/user_projects?username=${encodeURIComponent(user)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load projects');
                }
                return response.json();
            })
            .then(data => {
                const projectsList = document.getElementById('projects-list');
                projectsList.innerHTML = ''; // Clear existing projects
                data.projects.forEach(project => {
                    const projectLink = document.createElement('div');
                    projectLink.className = 'sidebar-item mb-2';
                    projectLink.textContent = project.name;

                    // Add click event to navigate to the project page
                    projectLink.addEventListener('click', () => {
                        window.location.href = `/project/${project.id}`;
                    });

                    projectsList.appendChild(projectLink);
                });
            })
            .catch(error => {
                console.error('Error fetching user projects:', error);
            });
    }

    // Function to display project details
    function displayProjectDetails(project) {
        const content = document.getElementById('content');
        content.innerHTML = `
            <h1>${project.name}</h1>
            <p>Details for project ID: ${project.id}</p>
        `;
    }

    // Initialize Create Project Modal
    const createProjectModal = new bootstrap.Modal(document.getElementById('createProjectModal'));

    // Handle create project button click
    document.getElementById('create-project').addEventListener('click', () => {
        createProjectModal.show();
    });

    // Handle create project form submission
    const createProjectForm = document.getElementById('createProjectForm');
    createProjectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const projectData = {
            name: document.getElementById('projectName').value,
            status: document.getElementById('projectStatus').value,
            tag: document.getElementById('projectTag').value,
            startDate: document.getElementById('projectStartDate').value,
            username: document.getElementById('usernameDisplay').textContent.replace('User: ', '')
        };

        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData),
            });

            if (response.ok) {
                const result = await response.json();
                alert('Project created successfully!');
                createProjectModal.hide();
                loadUserProjects(projectData.username); // Refresh the projects list
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error('Error creating project:', error);
            alert('Failed to create project. Please try again.');
        }
    });
});
