// modals.js

function initializeModals(refreshSidebarProjects) {
    // Initialize Create Project Modal
    const createProjectModalElement = document.getElementById('createProjectModal');
    if (createProjectModalElement) {
        const createProjectModal = new bootstrap.Modal(createProjectModalElement);
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
                endDate: document.getElementById('projectEndDate').value,
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
                    alert('Project created successfully!');
                    createProjectModal.hide();
                    if (refreshSidebarProjects) {
                        refreshSidebarProjects();
                    }
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                console.error('Error creating project:', error);
                alert('Failed to create project. Please try again.');
            }
        });
    }

    const createItemModalElement = document.getElementById('createItemModal');
    if (createItemModalElement) {
        const createItemModal = new bootstrap.Modal(createItemModalElement);
        document.getElementById('createItemButton').addEventListener('click', () => {
            createItemModal.show();
        });

        // Handle create item form submission
        const createItemForm = document.getElementById('createItemForm');
        createItemForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const projectId = document.getElementById('projectId').value;
            const itemData = {
                project_id: projectId,
                item_name: document.getElementById('itemName').value,
                type: document.getElementById('itemType').value,
                amount: document.getElementById('amount').value,
                category: document.getElementById('category').value,
                item_tag: document.getElementById('itemTag').value,
                startDate: document.getElementById('startDate').value,
                endDate: document.getElementById('endDate').value
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
                    if (refreshSidebarProjects) {
                        refreshSidebarProjects();
                    }
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                console.error('Error creating item:', error);
                alert('Failed to create item. Please try again.');
            }
        });
    }

    // Initialize Edit Item Modal
    const editItemModalElement = document.getElementById('editItemModal');
    if (editItemModalElement) {
        const editItemModal = new bootstrap.Modal(editItemModalElement);
        document.getElementById('editItemButton').addEventListener('click', async () => {
            const projectId = document.getElementById('editProjectId').value;

            try {
                const response = await fetch(`/api/project_items?projectId=${projectId}`);
                if (!response.ok) throw new Error('Failed to load items');

                const data = await response.json();
                const dropdown = document.getElementById('editItemDropdown');
                dropdown.innerHTML = ''; // Clear existing options

                if (data.items.length === 0) {
                    dropdown.innerHTML = '<option value="">No items available</option>';
                } else {
                    data.items.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = `${item.name} (${item.category})`;
                        dropdown.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error fetching items:', error);
                alert('Failed to load items. Please try again.');
            }

            editItemModal.show();
        });

        // Handle Edit Item form submission
        const editItemForm = document.getElementById('editItemForm');
        editItemForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const itemId = document.getElementById('editItemDropdown').value;
            const updatedItemData = {
                item_name: document.getElementById('editItemName').value,
                type: document.getElementById('editItemType').value,
                amount: document.getElementById('editAmount').value,
                category: document.getElementById('editCategory').value,
                startDate: document.getElementById('editStartDate').value,
                endDate: document.getElementById('editEndDate').value
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
                alert('Failed to update item. Please try again.');
            }
        });
    }

    // Initialize Remove Item Modal
    const removeItemModalElement = document.getElementById('removeItemModal');
    if (removeItemModalElement) {
        const removeItemModal = new bootstrap.Modal(removeItemModalElement);
        document.getElementById('removeItemButton').addEventListener('click', async () => {
            const projectId = document.getElementById('removeProjectId').value;

            try {
                const response = await fetch(`/api/project_items?projectId=${projectId}`);
                if (!response.ok) throw new Error('Failed to load items');

                const data = await response.json();
                const dropdown = document.getElementById('removeItemDropdown');
                dropdown.innerHTML = ''; // Clear existing options

                if (data.items.length === 0) {
                    dropdown.innerHTML = '<option value="">No items available</option>';
                } else {
                    data.items.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = `${item.name} (${item.category})`;
                        dropdown.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error fetching items:', error);
                alert('Failed to load items. Please try again.');
            }

            removeItemModal.show();
        });

        // Handle Remove Item form submission
        document.getElementById('removeItemForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const itemId = document.getElementById('removeItemDropdown').value;

            if (!itemId) {
                alert('Please select an item to remove.');
                return;
            }

            try {
                const response = await fetch(`/api/items/${itemId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    alert('Item removed successfully!');
                    removeItemModal.hide();
                    const projectId = document.getElementById('removeProjectId').value;
                    if (refreshSidebarProjects) {
                        refreshSidebarProjects();
                    }
                } else {
                    alert('Error removing item');
                }
            } catch (error) {
                console.error('Error removing item:', error);
                alert('Failed to remove item. Please try again.');
            }
        });
    }

}
