$(document).ready(function () {
    $(document)
        .on("click", ".org-name-div", function (event) {
            console.log(event)
            let element = $(event.currentTarget).closest(".organization");
            let text;
            element.children(".equipment-list").toggleClass("none");

            if (element.children(".equipment-list").hasClass("none")) {
                text = "+";
            } else {
                text = "-";
            }

            element.children("div").children(".toggle-button").html(text)
        })
        .on("input", "#search-input", function (event) {
            let element = $(event.currentTarget);
            var $elements = $(".organization-list").filter(function () {
                console.log($(this).html());
                return $(this).html() == element.val();
            });
        })
        .on("click", "#logout", function () {
            $.post("/backend/logout.php", {}, function () {
                location.reload();
            })
        })
        .on("click", "#add-element", function () {
            $("#popup").removeClass("none");
        })
        .on("change", "#select-add-element", function () {
            let id = "#add-" + $("#select-add-element").val();
            $(id).removeClass("none");
            $("form:not(" + id + ")").addClass("none");
            $("form input, form select").val(null);
        })
        .on("click", "#popup", function (event) {
            if (event.target.id !== "popup") return;

            $("#popup, form").addClass("none");
            $("form input, form select, #select-add-element").val(null);
        })
        .on("input", "input[type=\"number\"]", function (event) {
            if (Number($(event.currentTarget).val())) return;

            $(event.currentTarget).val(null);
        })
        .on("submit", "#add-equipment, #add-organization", function (event) {
            event.preventDefault();

            let element = event.currentTarget;
            let data = $(element).serialize();
            let type = element.id.replace("add-", "");
            // if($("#organization-" + array_data['organization_id'] + " li").length == 0) data['position'] = 1;

            $.post("/backend/elements/" + type + ".php", data)
                .done(function (response) {
                    $("#select-add-element").val(null);
                    console.log(response);
                    location.reload();
                });
        })

    // Находим поле ввода по его ID
    const searchInput = document.getElementById("search-input");

    // Находим все элементы списка организаций и техники
    const items = document.querySelectorAll(".organization, .equipment-list li");

    // Слушаем событие ввода в поле поиска
    searchInput.addEventListener("input", function () {
        const searchText = this.value.toLowerCase(); // Получаем текст из поля в нижнем регистре

        // Перебираем все элементы
        items.forEach((item) => {
            const text = item.textContent.toLowerCase(); // Получаем текст элемента в нижнем регистре

            // Проверяем, содержит ли элемент введенный текст в названии
            const containsText = text.includes(searchText);

            if (item.classList.contains("organization")) {
                // Если элемент - организация, проверяем наличие оборудования с текстом поиска
                const equipmentList = item.querySelector(".equipment-list");
                if (equipmentList) {
                    // Перебираем оборудование
                    const equipmentItems = equipmentList.querySelectorAll("li");
                    let hasMatchingEquipment = false;
                    equipmentItems.forEach((equipmentItem) => {
                        if (equipmentItem.textContent.toLowerCase().includes(searchText)) {
                            hasMatchingEquipment = true;
                        }
                    });

                    // Отображаем или скрываем организацию в зависимости от наличия соответствующего оборудования
                    if (hasMatchingEquipment || containsText) {
                        equipmentList.style.display = "block";
                    } else {
                        equipmentList.style.display = "none";
                    }
                }
            }

            // Отображаем или скрываем элемент в зависимости от наличия текста в названии
            if (containsText) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    });

    function deleteTab(tabId) {
        const tab = document.getElementById(tabId);
        const infoWindowId = `infoWindow-${tabId.replace("tab-", "")}`;
        const infoWindow = document.getElementById(infoWindowId);

        tab.remove();
        infoWindow.classList.remove("active");
    }

// Функция для создания кнопки удаления
    function createDeleteButton() {
        const deleteButton = document.createElement("button");

        // Устанавливаем вместо текста контента иконку (например, крестик)
        deleteButton.innerHTML = "&#10006;"; // Это HTML-код для символа "✖"

        deleteButton.classList.add("delete-button"); // Добавляем классы "delete-button" и "circle"

        return deleteButton;
    }

// Функция для создания вкладки с указанным именем и уникальным идентификатором
    function createTab(name) {
        const tab = document.createElement("div");
        tab.classList.add("machine-tab");
        tab.textContent = name;

        // Создаем кнопку удаления, вызывая отдельную функцию
        const deleteButton = createDeleteButton();

        // Добавляем кнопку удаления к вкладке
        tab.appendChild(deleteButton);

        // Добавляем обработчик клика для кнопки удаления
        deleteButton.addEventListener("click", (event) => {
            console.log("Клик по кнопке удаления");
            event.stopPropagation();

            // Получаем родительский элемент кнопки (вкладку)
            const tab = event.target.closest(".machine-tab");

            // Получаем идентификатор вкладки из её атрибута id
            const tabId = tab.id;

            // Вызываем функцию удаления вкладки
            deleteTab(tabId);
        });

        return tab;
    }

    function createInfoWindow(machineName, tag) {
        const decodedMachineName = decodeURIComponent(machineName);
        const infoWindowId = `infoWindow-${encodeURIComponent(decodedMachineName)}`;
        let infoWindow = document.getElementById(infoWindowId);
        if (tag == "label") {
            infoWindow = document.createElement("div"); //создание окна

            infoWindow.classList.add("machine-info");
            const machineDisplayName = decodedMachineName.replace('infoWindow-', '');
            infoWindow.innerHTML = `<h2 class="h2-style">${machineDisplayName}</h2>`;
        } else {
            infoWindow = document.createElement("div");
            infoWindow.classList.add("machine-info");
            const machineDisplayName = decodedMachineName.replace('infoWindow-', '');
            infoWindow.innerHTML = `
                <div class="div-stile">
                    <div class="description-container">
                        <h2 class="h2-style">${machineDisplayName}</h2>
                        <textarea class="description" placeholder="Добавьте описание"></textarea>
                    </div>
                    <div class="error-message">
                    </div>
                    <div class="protocols" style="display: flex; justify-content: space-between;">
                        <button class="save-button">Сохранить</button>
                        <input class="imei-input" placeholder="Введите IMEI">
                        <select class="protocolSelect field1">
                            <option disabled>Получение</option>
                            <option value="Wialon IPS">Wialon IPS</option>
                            <option value="GalileoSky">GalileoSky</option>
                        </select>
                        <select class="protocolSelect field2">
                            <option disabled>Отправление</option>
                            <option value="Wialon IPS">Wialon IPS</option>
                            <option value="GalileoSky">GalileoSky</option>
                        </select>
                    </div>
                </div>
                <div class="div-stile-status">
                    <div class="status-label0">Активность</div>
                    <div class="Status-bar">
                        <div class="status-gps status-label">gps<span class="status-dot1 status-dot"></span></div>
                        <div class="status-fuel status-label">fuel<span class="status-dot2 status-dot"></span></div>
                        <div class="status-data-sending status-label">Отправка<span class="status-dot3 status-dot"></span></div>
                        
                        <div class="status-label4 status-label">Задержка<span class="status-dot4">Ожидание</span></div>
                    </div>
                </divcl>
            `;
        }
        fetchDataAndUpdateLabels(decodedMachineName, infoWindow);

        // Добавляем созданное информационное окно к контейнеру
        const machineInfoContainer = document.querySelector(".windows-info");

        machineInfoContainer.appendChild(infoWindow);

        return infoWindow;
    }

    function updateStatus(imei, infoWindow) {
        function refreshStatus() {
            fetch(`backend/elements/get_status.php?imei=${imei}`)
                .then(response => response.json())
                .then(statusData => {
                    if (!statusData || Object.keys(statusData).length === 0) {
                        const errorMessage = infoWindow.querySelector('.error-message');
                        errorMessage.textContent = 'Устройство с таким IMEI не на связи или неверно введён IMEI';
                        return;
                    }

                    const { gps_status, fuel_status, data_sending, last_update } = statusData;

                    // Явное преобразование в целые числа
                    const gpsStatusInt = parseInt(gps_status);
                    const fuelStatusInt = parseInt(fuel_status);
                    const dataSendingInt = parseInt(data_sending);

                    // Обновление статусов GPS и топлива
                    const gpsDot = infoWindow.querySelector('.status-dot1');
                    const fuelDot = infoWindow.querySelector('.status-dot2');
                    const dataSendingDot = infoWindow.querySelector('.status-dot3');

                    // Сравнение с числами 0 и 1
                    gpsDot.style.backgroundColor = gpsStatusInt === 1 ? 'green' : 'red';
                    fuelDot.style.backgroundColor = fuelStatusInt === 1 ? 'green' : 'red';
                    dataSendingDot.style.backgroundColor = dataSendingInt === 1 ? 'green' : 'red';

                    // Преобразование времени из базы данных в объект Date
                    const lastUpdateDate = new Date(last_update);
                    const currentDate = new Date();
                    const delaySeconds = Math.floor((currentDate - lastUpdateDate) / 1000);
                    const days = Math.floor(delaySeconds / (24 * 60 * 60));
                    const hours = Math.floor((delaySeconds % (24 * 60 * 60)) / (60 * 60));
                    const minutes = Math.floor((delaySeconds % (60 * 60)) / 60);
                    const seconds = delaySeconds % 60;

                    let delayMessage = '';
                    if (days > 0) {
                        delayMessage += `${days} дн. `;
                    }
                    if (hours > 0) {
                        delayMessage += `${hours} час. `;
                    }
                    if (minutes > 0) {
                        delayMessage += `${minutes} мин. `;
                    }
                    delayMessage += `${seconds} сек.`;

                    const delayStatusDot = infoWindow.querySelector('.status-dot4');
                    delayStatusDot.textContent = delayMessage;
                    if (delaySeconds > 0) {
                        delayStatusDot.style.color = '#FFA500';
                    } else {
                        delayStatusDot.style.color = 'red';
                    }
                })
                .catch(error => console.error('Ошибка при обновлении статусов:', error));
        }

        // Инициализация первичного заполнения данных
        refreshStatus();
        setInterval(refreshStatus, 5000);
    }

    function fetchDataAndUpdateLabels(machineName, infoWindowElement) {
        const cleanedMachineName = machineName.replace('infoWindow-', '');
        fetch(`backend/elements/protocol.php?machineName=${encodeURIComponent(cleanedMachineName)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Полученные данные:', data);

                // Обновление значений полей
                const field1Select = infoWindowElement.querySelector('.protocolSelect.field1');
                const field2Select = infoWindowElement.querySelector('.protocolSelect.field2');
                const imeiInput = infoWindowElement.querySelector('.imei-input');
                const descriptionTextarea = infoWindowElement.querySelector('.description');

                field1Select.value = data.field_1;
                field2Select.value = data.field_2;
                imeiInput.value = data.imei;
                descriptionTextarea.value = data.description;

                console.log('Значение imeiInput после обновления:', imeiInput.value);
                updateStatus(imeiInput.value, infoWindowElement);
            })
            .catch(error => {
                console.error('Ошибка при получении данных:', error);
            });
    }

    const windowsInfoContainer = document.querySelector(".windows-info");
    windowsInfoContainer.addEventListener("click", function(event) {
        if (event.target.classList.contains("save-button")) {
            const userConfirmed = confirm("Вы уверены, что хотите сохранить изменения? Это повлиять на работу других интерфейсов.");

            if (!userConfirmed) {
                return;
            }

            const infoWindow = event.target.closest(".machine-info");
            const field1Select = infoWindow.querySelector(".protocolSelect.field1");
            const field2Select = infoWindow.querySelector(".protocolSelect.field2");
            const machineDisplayName = infoWindow.querySelector(".h2-style").textContent;
            // const parentId = infoWindow.id;
            const field1Value = field1Select.options[field1Select.selectedIndex].textContent;
            const field2Value = field2Select.options[field2Select.selectedIndex].textContent;
            const imeiInput = infoWindow.querySelector(".imei-input");
            const imeiValue = imeiInput.value;
            const description = infoWindow.querySelector(".description").value;

            fetch('/backend/elements/saveprotocol.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `
                    machineName=${encodeURIComponent(machineDisplayName)}
                    &field1=${encodeURIComponent(field1Value)}
                    &field2=${encodeURIComponent(field2Value)}
                    &imei=${encodeURIComponent(imeiValue)}
                    &description=${encodeURIComponent(description)}
                `.replace(/\s+/g, '')
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка HTTP: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message); // Отображаем сообщение об успешном сохранении
                    } else {
                        throw new Error(data.message); // Бросаем ошибку, если операция сохранения не удалась
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    alert("Произошла ошибка при сохранении данных.");
                });
        }
    });

    const equipmentButtons = document.querySelectorAll(".equipment");
    const machineTabs = document.querySelector(".machine-tabs");
    const machineInfoContainer = document.querySelector(".windows-info");

// Объект для отслеживания созданных вкладок и информационных окон
    const createdTabs = {};
    equipmentButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.stopPropagation(); // Остановка всплытия события на элементе .equipment

            const equipmentName = button.textContent.trim();
            const tabId = `tab-${encodeURIComponent(equipmentName)}`;
            const infoWindowId = `infoWindow-${encodeURIComponent(equipmentName)}`;
            const tagName = event.target.tagName.toLowerCase();

            // Добавляем обработчик события на элемент с классом "equipment"
            button.addEventListener("click", function (event) {
                event.stopPropagation(); // Остановка всплытия события, чтобы клик на элементе не срабатывал на родительском элементе
                // Добавьте ваш код обработки события для элемента .equipment
            });

            // Проверяем, существует ли уже вкладка с таким ID
            let tab = document.getElementById(tabId);

            if (!tab) {
                // Если вкладка не существует, создаем новую
                tab = createTab(equipmentName);
                tab.id = tabId;
                machineTabs.appendChild(tab);
            }

            // Проверяем, существует ли уже информационное окно с таким ID
            let infoWindow = document.getElementById(infoWindowId);

            if (!infoWindow) {
                // Если окно не существует, создаем новое
                infoWindow = createInfoWindow(infoWindowId, tagName);
                infoWindow.id = infoWindowId;
                machineInfoContainer.appendChild(infoWindow);
            }

            // Скрываем все информационные окна, кроме текущего
            const infoWindows = machineInfoContainer.querySelectorAll(".machine-info");
            infoWindows.forEach((window) => window.classList.remove("active"));
            infoWindow.classList.add("active");

            document.querySelectorAll(".machine-tab").forEach((tab) => tab.classList.remove("active"));
            tab.classList.add("active");

        });
    });

    machineTabs.addEventListener("click", (event) => {
        const clickedTab = event.target.closest(".machine-tab");

        if (clickedTab) {
            const equipmentName = clickedTab.id.replace("tab-", "");

            // Скрываем все информационные окна, кроме текущего
            const infoWindows = document.querySelectorAll(".machine-info");
            infoWindows.forEach((window) => window.classList.remove("active"));

            const infoWindow = document.getElementById(`infoWindow-${equipmentName}`);

            if (infoWindow) {
                // Показываем текущее информационное окно
                infoWindow.classList.add("active");

                // Убираем класс active у всех вкладок
                document.querySelectorAll(".machine-tab").forEach((tab) => tab.classList.remove("active"));

                // Добавляем класс active к текущей вкладке
                clickedTab.classList.add("active");
            }
        }
    });
})
