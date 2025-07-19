
// Search Memberships
function searchMemberships() {
  const memberId = document.getElementById('memberIdSearch').value;
  const plan = document.getElementById('planFilter').value;
  const status = document.getElementById('statusFilter').value;

  let queryParams = [];
  if (memberId) queryParams.push(`member_id=${memberId}`);
  if (plan) queryParams.push(`plan=${plan}`);
  if (status) queryParams.push(`status=${status}`);

  const queryString = queryParams.length ? '?' + queryParams.join('&') : '';

  fetch(`/admin/search_memberships${queryString}`)
  .then(response => response.json())
  .then(memberships => {
      const tableBody = document.getElementById('membershipsTableBody');
      tableBody.innerHTML = '';

      memberships.forEach(membership => {
          const row = `
              <tr>
                  <td>${membership.membership_id}</td>
                  <td>${membership.member_id}</td>
                  <td>${membership.plan}</td>
                  <td>${membership.purchase_date}</td>
                  <td>${membership.amount}</td>
                  <td>${membership.status}</td>
                  <td>
                      <button onclick="openUpdateModal(${membership.membership_id}, '${membership.plan}', ${membership.amount})">Update</button>
                      <button onclick="deleteMembership(${membership.membership_id})">Delete</button>
                  </td>
              </tr>
          `;
          tableBody.innerHTML += row;
      });
  });
}

// Update Membership Modal
function openUpdateModal(membershipId, currentPlan, currentAmount) {
  const modal = document.getElementById('updateModal');
  const form = document.getElementById('updateMembershipForm');
  
  document.getElementById('updateMembershipId').value = membershipId;
  form.querySelector('select[name="plan"]').value = currentPlan;
  form.querySelector('input[name="amount"]').value = currentAmount;
  
  modal.style.display = 'block';
}

// Close Modal
document.querySelector('.close').addEventListener('click', function() {
  document.getElementById('updateModal').style.display = 'none';
});

// Update Membership Form Submit
document.getElementById('updateMembershipForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  const membershipId = data.membership_id;

  fetch(`/update_membership/${membershipId}`, {
      method: 'PUT',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
      if (result.status === 'success') {
          alert('Membership updated successfully');
          searchMemberships();
          document.getElementById('updateModal').style.display = 'none';
      } else {
          alert('Error: ' + result.message);
      }
  });
});

// Delete Membership
function deleteMembership(membershipId) {
  if (confirm('Are you sure you want to delete this membership?')) {
      fetch(`/delete_membership/${membershipId}`, { method: 'DELETE' })
      .then(response => response.json())
      .then(result => {
          if (result.status === 'success') {
              alert('Membership deleted successfully');
              searchMemberships();
          } else {
              alert('Error: ' + result.message);
          }
      });
  }
}

// Initial load
searchMemberships();