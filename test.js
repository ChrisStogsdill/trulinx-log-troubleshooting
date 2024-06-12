let data = false;
let active = false;
let craftingData = false;
let hasXfixit = false;
//set to false to disable debugging
let debug = false;

//this lets us use debugLog instead of an if statement with console.log all over the place. 
function debugLog(...args) {
    if (debug) {
        console.log(...args);
    }
}

//main eventlistener that gets data from lua. idk how this shit works, I just bang my head against it and make changes until it isn't broke, then hope for the best..
window.addEventListener("message", function(event) {
    const item = event.data;
    debugLog("Received message:", item);

    if (item.action === "closeTablet") {
        $(".main-container").fadeOut("fast");
    }

    if (item.type === "showUI") {
        debugLog("Showing UI with data:", item);
        if (item.display) {
            data = item.data;
            hasXfixit = item.blueprints.includes("xfixit"); // Check if xfixit is included in blueprints
            debugLog("hasXfixit var", hasXfixit);
            $('.heading-name').html(item.playername);
            $('.skill-details').empty();
            $('.skill-details').append(`<div class="task-detail-bkg"></div>`);
            $(".main-container").fadeIn("fast");
            debugLog("Blueprints received:", item.blueprints);
            checkCraftingTabs(item.blueprints); // Pass blueprints to checkCraftingTabs
            Populate(data);
            openTab('home'); // Reset to home tab - exploit mitigation when blueprints are dropped but home isn't clicked
        } else {
            $(".main-container").fadeOut("fast");
        }
    }
	// if we show crafting info, set some vars
    if (item.type === "showCrafting") {
        debugLog("Showing crafting data:", item);
        if (item.display) {
            const craftingData = item.data;
            const nearBench = item.nearBench;
            const benchType = item.benchType;
			const craftingType = item.craftingType;
            debugLog("Crafting data received:", craftingData);
            debugLog("Bench status received:", { nearBench, benchType });
            PopulateCrafting(craftingData, nearBench, benchType, craftingType);
        } else {
            $(".main-container").fadeOut("fast");
        }
    }
	// if we show deconstruction info, set some vars
    if (item.type === "showDeconstruction") {
        debugLog("Showing deconstruction data:", item);
        if (item.display) {
            const deconstructionData = item.data;
			const nearBench = item.nearBench;
			const benchType = item.benchType;
            debugLog("Deconstruction data received:", deconstructionData);
            PopulateDeconstruction(deconstructionData, nearBench, benchType);
        } else {
            $(".main-container").fadeOut("fast");
        }
    }

    if (item.action === "setItemData") {
        debugLog("Received item data:", item.itemData);
        const { label, description, image } = item.itemData;
        $('#item-label').text(label);
        $('#item-description').text(description);
        $('#item-image').attr('src', `./assets/images/${image}`);
    }
});

//prints to log when the document is ready, usually on player server join or when the script is restarted
$(document).ready(function() {
    debugLog("Document ready");
});

//closes the tablet when the escape key is pressed
$(document).keyup(function(e) {
    if (e.key === "Escape") {
        debugLog("Escape key pressed");
        $(".main-container").fadeOut("fast");
        $.post(`https://${GetParentResourceName()}/exit`);
    }
});

//Populates the level data on the home tab
function Populate(data) {
    debugLog("Populating data:", data);
    $('.skills-main').empty();
    for (let i = 0; i < data.length; i++) {
        let html = `
        <div class="group" onmouseover="hover('${i}', true)" onmouseout="hover('${i}', false)" onclick="Expand('${i}')">
        <div class="group-4">
          <span class="trash-search">${data[i].taskname}</span>
        </div>
        <div class="rectangle" id="rectangle${i}"></div>
        <div class="group-5">
          <div class="level">
            <span class="level-6">Level | </span><span class="level-7">${data[i].currentlevel}</span>
          </div>
          <div class="exp">
            <span class="exp-8">Exp | </span><span class="exp-9">${data[i].currentexp}</span>
          </div>
          <div class="next-level">
            <span class="text-e">Next Level | </span><span class="number-200">${data[i].levelupexp}</span>
          </div>
        </div>
        <div role="progressbar" aria-valuenow="${data[i].percentage}" aria-valuemin="0" aria-valuemax="100" style="--value:${data[i].percentage}" class="circleprog-1"></div>
      </div>
        `;
        $('.skills-main').append(html);
    }
}

//when you hover over shit, changes background color. I can do this in css, but I'm an idiot who cant do frontend development, idk if this even works
function hover(x, enter) {
    if (active !== x) {
        if (enter) {
            $("#rectangle"+x).css('background-color', 'black');
        } else {
            $("#rectangle"+x).css('background-color', '#161717');
        }
    }
}

//triggered with populate later in the script, shows the task information on the right side bar
function Expand(x) {
    debugLog("Expanding item:", x);
    if (active) {
        $("#rectangle"+active).css('background-color', '#161717');
    }
    active = x;
    $("#rectangle"+x).css('background-color', 'black');
    $('.skill-details').empty();

    let id = Number(x);
    let qtyperks = data[id].perks.length;

    let html = `
    <span class="task-name">${data[id].taskname}</span>
        <div class="task-detail-img"></div>
        <div class="detail-prog-main">
          <div class="flex-row-e">
            <div class="detail-min">
              <span class="min-level">Min Level</span><span class="minnum">1</span>
            </div>
            <div class="detail-max">
              <span class="max-level">Max Level</span><span class="maxnum">${data[id].maxlevel}</span>
            </div>
          </div>
          <div role="progressbarlinear" aria-valuenow="${data[id].level_progress}" aria-valuemin="0" aria-valuemax="100" style="--value:${data[id].level_progress}" class="detail-prog-bar"></div>
        </div>
        <span class="task-desc"></span>
        <div class="task-detail-bkg"></div>
    `;
    $('.skill-details').append(html);

    for (let i = 0; i < qtyperks; i++) {
        let curperk = data[id].perks[i];
        $('.task-desc').append('◉ '+curperk+'</br>');
    }

    let background = `url(${data[id].task_img})`;
    $('.task-detail-img').css('background', background);
}

//Checks if the player has blueprints when the tablet is open to determine if the player has the ability to see the new tabs or not
function checkCraftingTabs(blueprints) {
    debugLog("Checking crafting tabs with blueprints:", blueprints);
    $(".weapons-bg").hide(); // Hide tabs by default
    $(".tools-bg").hide();
    $(".attachments-bg").hide();
    $(".deconstruction-bg").hide(); 

    if (Array.isArray(blueprints) && blueprints.length > 0) {
        debugLog("Blueprints are present:", blueprints);
        if (blueprints.includes("weapons_blueprints")) {
            debugLog("Showing weapons tab");
            $(".weapons-bg").show(); // show tabs if blueprints are in inventory
        }
        if (blueprints.includes("tools_blueprints")) {
            debugLog("Showing tools tab");
            $(".tools-bg").show();
        }
        if (blueprints.includes("attachments_blueprints")) {
            debugLog("Showing attachments tab");
            $(".attachments-bg").show();
        }
        if (blueprints.includes("xfixit")) {
            debugLog("Showing Deconstruction tab");
            $(".deconstruction-bg").show();
        }
    } else {
        debugLog("Blueprints data is empty or not an array.");
    }
}

//this is triggered when a user clicks on one of the new tabs. It does a post to requestCraftingData from NUI: requestCraftingData
function openTab(type) {
    debugLog("Opening tab:", type);
    $('.skills-main').hide();
    $('.crafting-main').hide();
    $('.skill-details').empty(); // Clear the skill details to avoid showing old data
    $('.item-details').hide(); // Hide the item details whenever switching tabs

    let dashboardTitle = '';
    switch(type) {
        case 'home':
            dashboardTitle = 'Level Details';
            $('.skills-main').show();
            break;
        case 'weapons':
            dashboardTitle = 'Weapon Crafting';
            break;
        case 'tools':
            dashboardTitle = 'Tools Crafting';
            break;
        case 'attachments':
            dashboardTitle = 'Attachment Crafting';
            break;
        case 'deconstruction':
            dashboardTitle = 'Item Deconstruction';
            break;
        default:
            dashboardTitle = 'Dashboard';
            break;
    }
    $('.dashboard-title').text(dashboardTitle);

    if (type !== 'home') {
        debugLog("Sending request for crafting data:", type);
        if (type === 'deconstruction') {
            $.post(`https://${GetParentResourceName()}/requestDeconstructionData`, JSON.stringify({ type: type }), function(response) { //send to lua to collect data
                debugLog("Received deconstruction data:", response.data);
                PopulateDeconstruction(response.data, response.nearBench, response.benchType);
            });
        } else {
            $.post(`https://${GetParentResourceName()}/requestCraftingData`, JSON.stringify({ type: type }), function(response) { //send to lua to collect data
                debugLog("Received crafting data:", response.data);
                PopulateCrafting(response.data, response.nearBench, response.benchType, response.craftingType);
            });
        }
    }
}

//first stop to getting item data.
function PopulateCrafting(craftingData, nearBench, benchType, craftingType) {
    debugLog("Populating crafting data:", craftingData);
    $('.crafting-list').empty();
    
    debugLog("Bench status nearBench:", nearBench);
    debugLog("Bench status benchType:", benchType);
    debugLog("Current tab:", craftingType);

    let benchStatus = '';
    if (nearBench) {
        if (benchType.toLowerCase() === craftingType) {
            benchStatus = '<span style="color: green;">Bench</span>';
        } else {
            benchStatus = '<span style="color: red;">Bench</span>';
        }
    } else {
        benchStatus = '<span style="color: red;">Bench</span>';
    }
	
    if (craftingData && craftingData.length > 0) {
        // Group items by level
        let itemsByLevel = {};
        for (let i = 0; i < craftingData.length; i++) {
            let item = craftingData[i].data;
            let itemName = craftingData[i].itemName;
            let level = item.requirements.level_required || 1;
            
            if (!itemsByLevel[level]) {
                itemsByLevel[level] = [];
            }
            itemsByLevel[level].push({ itemName, item });
        }

        // Generate HTML for each level
        for (let level in itemsByLevel) {
            if (itemsByLevel.hasOwnProperty(level)) {
                let levelHeader = `<h3>Level ${level}</h3>`;
                $('.crafting-list').append(levelHeader);

                // Sort items alphabetically by item.label
                itemsByLevel[level].sort((a, b) => a.item.label.localeCompare(b.item.label));

                itemsByLevel[level].forEach(craftingItem => {
                    let item = craftingItem.item;
                    let itemName = craftingItem.itemName;
                    let html = `
                    <div class="crafting-item" onclick='showItemDetails("${itemName}", ${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                      <span class="item-name">${item.label}</span>
                    </div>
                    `;
                    $('.crafting-list').append(html);
                });
            }
        }

        $('.crafting-main').show();
    } else {
        debugLog("No crafting data available to populate.");
    }
	// Update bench status in dashboard title
	let currentTitle = $('.dashboard-title').text().split(" - ")[0]; // Get the current title without the status
    $('.dashboard-title').html(`${currentTitle} - ${benchStatus}`);
}

//first stop to getting deconstructable item data
function PopulateDeconstruction(deconstructionData, nearBench, benchType) {
    debugLog("DEBUG: Populating deconstruction data:", deconstructionData);
    $('.crafting-list').empty();
	debugLog("Bench status nearBench:", nearBench);
	let benchStatus = '';
	if (nearBench) {
        if (benchType.toLowerCase() === "deconstruct") {
            benchStatus = '<span style="color: green;">Bench</span>';
        } else {
            benchStatus = '<span style="color: red;">Bench</span>';
        }
    } else {
        benchStatus = '<span style="color: red;">Bench</span>';
    }
    if (deconstructionData && deconstructionData.length > 0) {
        // Sort items alphabetically by item.label
        deconstructionData.sort((a, b) => a.label.localeCompare(b.label));
		
        deconstructionData.forEach(deconstructionItem => {
            let itemName = deconstructionItem.itemName;
            let itemLabel = deconstructionItem.label;
            debugLog("DEBUG: Processing deconstruction item:", deconstructionItem);
            let html = `
            <div class="crafting-item" onclick='showDeconstructionDetails("${itemName}", ${JSON.stringify(deconstructionItem).replace(/'/g, "&apos;")})'>
              <span class="item-name">${itemLabel}</span>
            </div>
            `;
            $('.crafting-list').append(html);
        });

        $('.crafting-main').show();
    } else {
        debugLog("DEBUG: No deconstruction data available to populate.");
    }
	// Update bench status in dashboard title
    let currentTitle = $('.dashboard-title').text().split(" - ")[0]; // Get the current title without the status
    $('.dashboard-title').html(`${currentTitle} - ${benchStatus}`);
}


//This fills out the crafting menu with items and pulls the item image using nui:// from qb-inventory
//todo: change default.png to some other real image.... like a proj x maybe?

//removed this div for now, I want to see what it looks like: <div class="item-description">${item.description}</div>
// show item details when an item to construct is clicked on
function showItemDetails(itemName, item) {
    debugLog("Showing details for item:", itemName, item);
    $('.item-details').empty();

    // Log the entire item object for debugging
    debugLog("Item object:", JSON.stringify(item, null, 2));

    // Use the nui protocol to access the image
    let imagePath = item.image ? `nui://qb-inventory/html/images/${item.image}` : 'nui://qb-inventory/html/images/default.png';
    debugLog("Constructed image path:", imagePath);

    // Request inventory check for the item materials
    $.post(`https://${GetParentResourceName()}/checkinventoryitems`, JSON.stringify({ itemName: itemName }), function(response) {
        debugLog("Inventory check response:", JSON.stringify(response, null, 2));
        
        // Construct HTML for item details
        let materialsHtml = `
        <span>Materials:</span>
        ${item.materials.map(material => {
            let inventoryItem = response.items.find(invItem => invItem.name === material.name);
            let inventoryAmount = inventoryItem ? inventoryItem.amount : 0;
            let materialLabel = material.label || material.name; // Ensure we use the material label
            return `<div>${material.amount}x ${materialLabel} (inv:${inventoryAmount})</div>`;
        }).join('')}
        `;

        let html = `
        <div class="item-detail">
            <span class="item-name">${item.label}</span>
            <div class="item-image" style="background-image: url('${imagePath}');"></div>
            
            <div class="item-materials">${materialsHtml}</div>
            <div class="item-quantity">
                <span>Quantity:</span>
                <input type="number" id="quantity-input" value="1" min="1">
            </div>
            <button class="craft-button" onclick="attemptCraft('${itemName}')">Craft</button>
        </div>
        `;
        $('.item-details').append(html);
        $('.item-details').show(); // Unhide the item-details element

        // Add event listener for input changes to update materials (is this needed anymore???)
        document.getElementById('quantity-input').addEventListener('input', function() {
            debugLog("Quantity input changed:", this.value);
            updateMaterials(itemName, item, response.items);
        });

        // Call updateMaterials initially to set the correct button state
        updateMaterials(itemName, item, response.items);
    });
}

//When deconstructing - showing details of the item when it's clicked on
function showDeconstructionDetails(itemName, item) {
    debugLog("DEBUG: Showing details for deconstruction item:", itemName, item);
    $('.item-details').empty();

    // Log the entire item object for debugging
    debugLog("DEBUG: Item object:", JSON.stringify(item, null, 2));

    // Use the nui protocol to access the image
    let imagePath = item.image ? `nui://qb-inventory/html/images/${item.image}` : 'nui://qb-inventory/html/images/default.png';
    debugLog("DEBUG: Item selected: ", item.itemName);
    debugLog("DEBUG: Constructed image path:", imagePath);

    let materialsHtml = `
    <span>Materials received:</span>
    ${(item.materials && item.materials.length > 0) ? item.materials.map(material => `<div>${material.amount}x ${material.label}</div>`).join('') : '<div>+1 XP</div>'}
    `;

    let html = `
    <div class="item-detail">
        <span class="item-name">${item.label}</span>
        <div class="item-image" style="background-image: url('${imagePath}');"></div>
        <div class="item-materials">${materialsHtml}</div>
        <button class="deconstruct-button" onclick="attemptDeconstruct('${itemName}')">Deconstruct</button>
    </div>
    `;
    debugLog("DEBUG: Generated HTML for item details:", html);
    $('.item-details').append(html);
    $('.item-details').show(); // Unhide the item-details element
}


//This is supposed to update the value to craft certain items, but for some reason it doesn't do shit unless you press enter (which I added in the showItemDetails script above)
function updateMaterials(itemName, item, inventoryItems) {
    let quantity = parseInt(document.getElementById('quantity-input').value, 10);
    debugLog("Updating materials with quantity:", quantity);

    let hasAllMaterials = true; // Flag to check if player has all required materials
    let materialsHtml = `
    <span>Materials:</span>
    ${item.materials.map(material => {
        let inventoryItem = inventoryItems.find(invItem => invItem.name === material.name);
        let inventoryAmount = inventoryItem ? inventoryItem.amount : 0;
        let requiredAmount = material.amount * quantity;
        let materialLabel = material.label || material.name; // Ensure we use the material label
        if (inventoryAmount < requiredAmount) {
            hasAllMaterials = false; // Player doesn't have enough of this material
        }
        return `<div>${requiredAmount}x ${materialLabel} (You Have: ${inventoryAmount})</div>`;
    }).join('')}
    `;

    // Update the materials HTML
    let materialsContainer = document.querySelector('.item-materials');
    materialsContainer.style.display = 'none'; // Hide the container
    materialsContainer.innerHTML = ''; // Clear existing content
    materialsContainer.innerHTML = materialsHtml; // Set new content
    materialsContainer.style.display = 'block'; // Show the container

    // Update the craft button color and state
    let craftButton = document.querySelector('.craft-button');
    if (hasAllMaterials) {
        craftButton.classList.remove('red');
        craftButton.classList.add('green');
        craftButton.disabled = false; // Enable the button
    } else {
        craftButton.classList.remove('green');
        craftButton.classList.add('red');
        craftButton.disabled = true; // Disable the button
    }
}

//button to attempt to deconstruct the item
function attemptDeconstruct(itemName) {
    debugLog("Attempting to deconstruct item:", itemName);

    // Send message to close the tablet
    $(".main-container").fadeOut("fast");
    $.post(`https://${GetParentResourceName()}/exit`); //does this work? tab closes, but maybe that's just in lua now?

    // Proceed with deconstruction
    $.post(`https://${GetParentResourceName()}/deconstructItem`, JSON.stringify({ item: itemName }), function(response) {
        debugLog("Deconstruction response:", response);
    });
}

//This sends whatever is being crafted with whatever quantity to NUICallback: craftItem
function attemptCraft(itemName) {
    let quantity = parseInt(document.getElementById('quantity-input').value, 10);
    debugLog("Attempting to craft item:", itemName, "Quantity:", quantity);
    
    // Send message to close the tablet
    $(".main-container").fadeOut("fast");
    $.post(`https://${GetParentResourceName()}/exit`); 

    // Proceed with crafting
    $.post(`https://${GetParentResourceName()}/craftItem`, JSON.stringify({ item: itemName, quantity: quantity }), function(response) {
        debugLog("Crafting response:", response);
    });
}
