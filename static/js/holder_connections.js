document.addEventListener('DOMContentLoaded', async () => {
  const connectionsTable = document.getElementById('connectionsTable');
  const noConnections = document.getElementById('noConnections');
  const successMessage = document.getElementById('success-message');
  const errorMessage = document.getElementById('error-message');

  // Hide messages initially
  successMessage.classList.add('hidden');
  errorMessage.classList.add('hidden');
  noConnections.classList.add('hidden');

  try {
    const response = await fetch('/connections/holder', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    // The array of connections is in data.results
    const connections = data.results || [];

    if (connections.length === 0) {
      noConnections.classList.remove('hidden');
      return;
    }

    // Clear existing rows
    connectionsTable.innerHTML = '';

    connections.forEach(connection => {
      const row = document.createElement('tr');
      row.className = 'border-t border-gray-200 hover:bg-gray-50';

      // Format dates nicely
      const createdAt = new Date(connection.created_at).toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
      const updatedAt = new Date(connection.updated_at).toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });

      row.innerHTML = `
        <td class="p-3">${connection.their_label}</td>
        <td class="p-3">
          <span class="inline-block px-2 py-1 text-xs font-semibold rounded-full
            ${connection.state === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
            ${connection.state}
          </span>
        </td>
        <td class="p-3 font-mono text-sm">${connection.connection_id}</td>
        <td class="p-3 font-mono text-sm">${connection.their_did}</td>
        <td class="p-3">${createdAt}</td>
        <td class="p-3">${updatedAt}</td>
        <td class="p-3">
          <a href="/messenger/${connection.connection_id}"
             class="bg-indigo-600 text-white px-3 py-1 rounded-lg hover:bg-indigo-700 transition duration-200">
            Message
          </a>
        </td>
      `;
      connectionsTable.appendChild(row);
    });

  } catch (error) {
    errorMessage.textContent = `Error fetching connections: ${error.message}`;
    errorMessage.classList.remove('hidden');
  }
});
