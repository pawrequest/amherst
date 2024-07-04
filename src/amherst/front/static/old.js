function toggleContainer(containerId) {
    const containers = document.querySelectorAll('.record-container');
    containers.forEach(container => {
        if (container.id === containerId) {
            container.classList.toggle('expanded');
        } else {
            container.classList.remove('expanded');
        }
    });
}