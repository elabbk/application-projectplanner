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

    // Initialize modals for creating and editing items
    const createItemModal = new bootstrap.Modal(document.getElementById('createItemModal'));
    const editItemModal = new bootstrap.Modal(document.getElementById('editItemModal'));
    const removeItemModal = new bootstrap.Modal(document.getElementById('removeItemModal'));

    // Handle Create Item button click
    document.getElementById('createItemButton').addEventListener('click', () => {
        createItemModal.show();
    });

    // Handle Edit Item button click
    document.getElementById('editItemButton').addEventListener('click', () => {
        const projectId = document.getElementById('editProjectId').value;
        fetch(`/api/items/${projectId}`)
            .then(response => response.json())
            .then(data => {
                const dropdown = document.getElementById('editItemDropdown');
                dropdown.innerHTML = ''; // Clear existing options
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.name;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching items:', error));

        editItemModal.show();
    });

    // Handle Remove Item button click
    document.getElementById('removeItemButton').addEventListener('click', () => {
        const projectId = document.getElementById('editProjectId').value;
        fetch(`/api/items/${projectId}`)
            .then(response => response.json())
            .then(data => {
                const dropdown = document.getElementById('removeItemDropdown');
                dropdown.innerHTML = ''; // Clear existing options
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.name;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching items:', error));

        removeItemModal.show();
    });

    // Handle Create Item form submission
    document.getElementById('createItemForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const projectId = document.getElementById('projectId').value;
        const itemData = {
            project_id: projectId,
            item_name: document.getElementById('itemName').value,
            type: document.getElementById('itemType').value
        };

        try {
            const response = await fetch('/api/items', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(itemData)
            });

            if (response.ok) {
                alert('Item created successfully!');
                createItemModal.hide();
            } else {
                alert('Error creating item');
            }
        } catch (error) {
            console.error('Error creating item:', error);
        }
    });

    // Handle Edit Item form submission
    document.getElementById('editItemForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const itemId = document.getElementById('editItemDropdown').value;
        const updatedItemData = {
            item_name: document.getElementById('editItemName').value,
            type: document.getElementById('editItemType').value
        };

        try {
            const response = await fetch(`/api/items/${itemId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedItemData)
            });

            if (response.ok) {
                alert('Item updated successfully!');
                editItemModal.hide();
            } else {
                alert('Error updating item');
            }
        } catch (error) {
            console.error('Error updating item:', error);
        }
    });

    // Handle Remove Item form submission
    document.getElementById('removeItemForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const itemId = document.getElementById('removeItemDropdown').value;

        try {
            const response = await fetch(`/api/items/${itemId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                alert('Item removed successfully!');
                removeItemModal.hide();

                // Optionally refresh the item list
                const projectId = document.getElementById('removeProjectId').value;
                loadProjectItems(projectId);
            } else {
                alert('Error removing item');
            }
        } catch (error) {
            console.error('Error removing item:', error);
            alert('Failed to remove item. Please try again.');
        }
    });

});
