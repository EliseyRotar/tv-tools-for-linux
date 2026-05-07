// Settings Management JavaScript

// Check scrcpy on page load
document.addEventListener('DOMContentLoaded', function() {
    checkScrcpy();
});

async function setScreenTimeout() {
    const timeout = document.getElementById('screenTimeout').value;
    
    if (!timeout || timeout < 0) {
        showToast('Please enter a valid timeout value', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/settings/set', {
            name: 'screen_timeout',
            value: timeout
        });
        
        if (response.success) {
            showToast('Screen timeout updated successfully', 'success');
        } else {
            showToast('Failed to update screen timeout: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error setting screen timeout:', error);
        showToast('Error setting screen timeout: ' + error.message, 'error');
    }
}

async function setAnimationScale() {
    const scale = document.getElementById('animationScale').value;
    
    try {
        const response = await api.post('/api/settings/set', {
            name: 'animation_scale_window',
            value: scale
        });
        
        if (response.success) {
            // Set all animation scales
            await api.post('/api/settings/set', {
                name: 'animation_scale_transition',
                value: scale
            });
            
            await api.post('/api/settings/set', {
                name: 'animation_scale_animator',
                value: scale
            });
            
            showToast('Animation scale updated successfully', 'success');
        } else {
            showToast('Failed to update animation scale: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error setting animation scale:', error);
        showToast('Error setting animation scale: ' + error.message, 'error');
    }
}

async function toggleGPS(enable) {
    try {
        const value = enable ? 'gps,network' : '';
        const response = await api.post('/api/settings/set', {
            name: 'gps_location',
            value: value
        });
        
        if (response.success) {
            showToast(`GPS ${enable ? 'enabled' : 'disabled'} successfully`, 'success');
        } else {
            showToast(`Failed to ${enable ? 'enable' : 'disable'} GPS: ` + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling GPS:', error);
        showToast('Error toggling GPS: ' + error.message, 'error');
    }
}

async function toggleAutoUpdates(enable) {
    try {
        const value = enable ? '0' : '1';
        const response = await api.post('/api/settings/set', {
            name: 'auto_updates',
            value: value
        });
        
        if (response.success) {
            showToast(`Auto updates ${enable ? 'enabled' : 'disabled'} successfully`, 'success');
        } else {
            showToast(`Failed to ${enable ? 'enable' : 'disable'} auto updates: ` + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling auto updates:', error);
        showToast('Error toggling auto updates: ' + error.message, 'error');
    }
}

async function toggleStayAwake(enable) {
    try {
        const value = enable ? '7' : '0';
        const response = await api.post('/api/settings/set', {
            name: 'stay_awake',
            value: value
        });
        
        if (response.success) {
            showToast(`Stay awake ${enable ? 'enabled' : 'disabled'} successfully`, 'success');
        } else {
            showToast(`Failed to ${enable ? 'enable' : 'disable'} stay awake: ` + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling stay awake:', error);
        showToast('Error toggling stay awake: ' + error.message, 'error');
    }
}

async function checkScrcpy() {
    try {
        const response = await api.get('/api/remote/check');
        
        if (response.success) {
            const statusDiv = document.getElementById('scrcpyStatus');
            const statusText = document.getElementById('scrcpyStatusText');
            
            if (response.installed) {
                statusDiv.className = 'alert alert-success';
                statusText.textContent = `scrcpy is installed (${response.version || 'version unknown'})`;
            } else {
                statusDiv.className = 'alert alert-warning';
                statusText.textContent = 'scrcpy is not installed. Install it to use remote control features.';
            }
            
            statusDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error checking scrcpy:', error);
    }
}

async function launchScrcpy() {
    const preset = document.getElementById('scrcpyPreset').value;
    
    try {
        const response = await api.post('/api/remote/launch', {
            preset: preset
        });
        
        if (response.success) {
            showToast('scrcpy launched successfully', 'success');
        } else {
            showToast('Failed to launch scrcpy: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error launching scrcpy:', error);
        showToast('Error launching scrcpy: ' + error.message, 'error');
    }
}
