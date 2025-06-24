const load_departments = () => {
    fetch("http://127.0.0.1:8000/department/")
      .then((res) => res.json())
      .then((data) => display_departments(data))
      .catch((err) => console.log(err));
  };
load_departments();

const display_departments = (departments) => {
  console.log(departments);
  departments.forEach((department) => {
    console.log(department);
    
    const parent = document.getElementById("department-container");
    const a = document.createElement("a");
    a.innerHTML = `
      <a
            href="#"
            class="block w-full px-4 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:border-gray-600 dark:hover:bg-gray-600 dark:hover:text-white dark:focus:ring-gray-500 dark:focus:text-white"
          >
            ${department.name}
          </a>
      `;
    parent.appendChild(a);
  });
};
