// scripts.js

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

    // Handle Overview click to prevent full page reload
    document.getElementById('overview').addEventListener('click', () => {
        const content = document.getElementById('content');
        content.innerHTML = `
            <h1>Overview</h1>
            <p>Welcome to your project overview. Please select a project from the sidebar.</p>
        `;

        const username = localStorage.getItem('username');
        if (username) {
            loadUserProjects(username);
        } else {
            alert('Please set your username first.');
        }
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

    // Function to refresh the sidebar project list dynamically
    function refreshSidebarProjects() {
        const username = localStorage.getItem('username');
        if (username) {
            loadUserProjects(username);
        }
    }

    // Load modals from modals.js
    initializeModals(refreshSidebarProjects);
});
