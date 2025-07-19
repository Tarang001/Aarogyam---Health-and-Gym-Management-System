
function searchStaff() {
  const query = document.getElementById('searchQuery').value;
  const department = document.getElementById('departmentFilter').value;

  fetch(`/search_staff?query=${query}&department=${department}`)
  .then(response => response.json())
  .then(staff => {
      const tableBody = document.getElementById('staffTableBody');
      tableBody.innerHTML = '';  // Clear previous results

      staff.forEach(member => {
          const row = `
              <tr>
                  <td>${member.first_name} ${member.last_name}</td>
                  <td>${member.email}</td>
                  <td>${member.phone}</td>
                  <td>${member.salary}</td>
                  <td>${member.department}</td>
                  <td>
                      <button onclick="deleteStaff(${member.id})">Delete</button>
                  </td>
              </tr>
          `;
          tableBody.innerHTML += row;
      });
  });
}

function deleteStaff(staffId) {
  if (confirm('Are you sure you want to delete this staff member?')) {
      fetch(`/delete_staff/${staffId}`, { method: 'DELETE' })
      .then(response => response.json())
      .then(result => {
          if (result.status === 'success') {
              alert('Staff member deleted');
              searchStaff();  // Refresh the list
          } else {
              alert('Error: ' + result.message);
          }
      });
  }
}

// Initial load
searchStaff();