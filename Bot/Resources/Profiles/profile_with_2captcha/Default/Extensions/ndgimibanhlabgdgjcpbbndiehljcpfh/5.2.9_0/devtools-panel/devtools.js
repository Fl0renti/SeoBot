var isFirefox="undefined"!==typeof InstallTrigger,browserType=chrome;isFirefox&&(browserType=browser);var connectBackgroundPage=browserType.runtime.connect({name:"devtools-page"});browserType.devtools.panels.elements.createSidebarPane("SelectorsHub",function(a){a.setPage("../devtools-panel/shub-panel.html");a.onShown.addListener(openedTab);a.onHidden.addListener(closedTab)});function openedTab(){browserType.runtime.sendMessage({message:"generate-selector"})}
function closedTab(){connectBackgroundPage.postMessage({name:"highlight-element",tabId:browserType.devtools.inspectedWindow.tabId,xpath:["xpath","//sanjay",!1]})};
