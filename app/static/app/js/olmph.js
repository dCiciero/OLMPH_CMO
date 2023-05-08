document.addEventListener('DOMContentLoaded', () => {
    let btn_export_csv = document.querySelector('#btn_export');
    let btn_prev = document.querySelector('#btn_prev');
    let fin_tab = document.querySelector('#financeTab');
    search_exco = document.querySelector('#txt_search_exco')
    search_member = document.querySelector('#txt_search_individual_acct')
    tbl_account = document.querySelector('#tbl_members_acct')
    memberDetails = document.querySelector('#txt_search_member_details')
    tblDetails = document.querySelector('#tbl_member_details');
    cmbState = document.querySelector('#drp_state');


    if (search_member != null){
        search_member.onkeyup = () =>{
            memberLookup(search_member, tbl_account)
            // console.log(search_member.value)
        }
    }
    if (memberDetails != null){
        memberDetails.onkeyup = () =>{
            memberLookup(memberDetails, tblDetails)
            // console.log(memberDetails.value)
        }
    }
    if (cmbState != null) {
        cmbState.onchange = () => {
            console.log(cmbState.value)
        }
    }

    if (btn_export_csv != null){
        btn_export_csv.onclick = (e) => {
            // alert('exporting to csv');
            console.log('exporting to csv');
        }
    }
    if (btn_prev != null){
        btn_prev.onclick = (e) => {
            e.preventDefault();
            console.log('new reform');
        }
    }

    function memberLookup(name, tablename){
        // console.log(tablename);
        let filter, table, tr, td, i, txtValue;
        input = name; // document.getElementById(`${name}`);
        filter = input.value.toUpperCase();
        table = tablename;  //document.getElementById(`${tablename}`);
        tr = table.getElementsByTagName("tr");

        // Loop through all table rows, and hide those who don't match the search query
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[1];
            if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
            }
        }
    }

    // fin_tab.onclick = (e) => {
    //     e.preventDefault();
    //     console.log('Hey');
    // }
    
    // $('#financeTab a').on('click', function (e) {
    //     e.preventDefault()
    //     alert("hey")
    //     $(this).tab('show')
    // })
})