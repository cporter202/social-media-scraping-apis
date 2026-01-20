/**
 * Script to fetch all Apify Actors from the API and compile them into a list
 * with affiliate links.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_BASE_URL = 'api.apify.com';
const AFFILIATE_PARAM = '?fpr=p2hrc6';

/**
 * Make HTTP GET request
 */
function makeRequest(url, path) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: url,
            path: path,
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve(jsonData);
                } catch (e) {
                    reject(new Error(`Failed to parse JSON: ${e.message}`));
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.end();
    });
}

/**
 * Fetch all actors from Apify Store API with pagination
 */
async function fetchAllActors(limit = 100) {
    const allActors = [];
    let offset = 0;
    let totalFetched = 0;

    console.log('Starting to fetch Apify Actors...');
    console.log('='.repeat(60));

    while (true) {
        try {
            const path = `/v2/store?limit=${limit}&offset=${offset}`;
            console.log(`Fetching actors at offset ${offset}...`);

            const data = await makeRequest(API_BASE_URL, path);

            // Extract actors from response
            const actors = data?.data?.items || [];

            if (!actors || actors.length === 0) {
                console.log(`No more actors found at offset ${offset}`);
                break;
            }

            // Process each actor
            for (const actor of actors) {
                const actorInfo = {
                    name: actor.name || 'Unknown',
                    username: actor.username || '',
                    title: actor.title || actor.name || 'Unknown',
                    description: actor.description || '',
                    url: actor.url || '',
                    affiliate_url: '',
                    stats: actor.stats || {},
                    categories: actor.categories || [],
                    createdAt: actor.createdAt || '',
                    modifiedAt: actor.modifiedAt || ''
                };

                // Create affiliate URL
                if (actorInfo.url) {
                    // Check if URL already has query parameters
                    const separator = actorInfo.url.includes('?') ? '&' : '?';
                    actorInfo.affiliate_url = `${actorInfo.url}${separator}fpr=p2hrc6`;
                } else {
                    // Construct URL from username and name if URL is missing
                    if (actorInfo.username && actorInfo.name) {
                        actorInfo.url = `https://apify.com/${actorInfo.username}/${actorInfo.name}`;
                        actorInfo.affiliate_url = `${actorInfo.url}?fpr=p2hrc6`;
                    }
                }

                allActors.push(actorInfo);
            }

            totalFetched += actors.length;
            const totalCount = data?.data?.total || 0;
            console.log(`Fetched ${totalFetched} actors so far... (Total available: ${totalCount})`);

            // Check if we've reached the end
            if (offset + actors.length >= totalCount) {
                console.log(`Reached end. Total actors: ${totalCount}`);
                break;
            }

            offset += limit;

            // Be respectful with API rate limits
            await new Promise(resolve => setTimeout(resolve, 500));

        } catch (error) {
            console.error(`Error fetching actors at offset ${offset}: ${error.message}`);
            console.log('Retrying in 5 seconds...');
            await new Promise(resolve => setTimeout(resolve, 5000));
            continue;
        }
    }

    console.log(`\nTotal actors fetched: ${allActors.length}`);
    return allActors;
}

/**
 * Save actors data to JSON file
 */
function saveToJSON(actors, filename = 'apify_actors.json') {
    const filePath = path.join(__dirname, '..', filename);
    fs.writeFileSync(filePath, JSON.stringify(actors, null, 2), 'utf-8');
    console.log(`Saved ${actors.length} actors to ${filename}`);
}

/**
 * Generate a markdown file with all actors and affiliate links
 */
function generateMarkdownList(actors, filename = 'APIFY_ACTORS.md') {
    let content = `# Apify Actors List\n\n`;
    content += `Complete list of ${actors.length} Apify Actors (APIs) available on the Apify platform.\n\n`;
    content += `---\n\n`;

    // Group by category if available
    const actorsByCategory = {};
    const uncategorized = [];

    for (const actor of actors) {
        const categories = actor.categories || [];
        if (categories.length > 0) {
            for (const category of categories) {
                if (!actorsByCategory[category]) {
                    actorsByCategory[category] = [];
                }
                actorsByCategory[category].push(actor);
            }
        } else {
            uncategorized.push(actor);
        }
    }

    // Write categorized actors
    const sortedCategories = Object.keys(actorsByCategory).sort();
    for (const category of sortedCategories) {
        content += `## ${category}\n\n`;
        const sortedActors = actorsByCategory[category].sort((a, b) => 
            (a.title || '').localeCompare(b.title || '')
        );
        
        for (const actor of sortedActors) {
            const title = actor.title || actor.name || 'Unknown';
            const affiliateUrl = actor.affiliate_url || actor.url || '';
            const description = actor.description || '';

            if (description) {
                content += `- **[${title}](${affiliateUrl})** - ${description}\n`;
            } else {
                content += `- **[${title}](${affiliateUrl})**\n`;
            }
        }
        content += '\n';
    }

    // Write uncategorized actors
    if (uncategorized.length > 0) {
        content += `## Uncategorized\n\n`;
        const sortedUncategorized = uncategorized.sort((a, b) => 
            (a.title || '').localeCompare(b.title || '')
        );
        
        for (const actor of sortedUncategorized) {
            const title = actor.title || actor.name || 'Unknown';
            const affiliateUrl = actor.affiliate_url || actor.url || '';
            const description = actor.description || '';

            if (description) {
                content += `- **[${title}](${affiliateUrl})** - ${description}\n`;
            } else {
                content += `- **[${title}](${affiliateUrl})**\n`;
            }
        }
        content += '\n';
    }

    content += `---\n\n`;
    content += `*Total: ${actors.length} Actors*\n`;
    content += `*Last updated: ${new Date().toISOString().split('T')[0]} ${new Date().toTimeString().split(' ')[0]}*\n`;

    const filePath = path.join(__dirname, '..', filename);
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`Generated markdown list: ${filename}`);
}

/**
 * Generate a simple text file with just names and affiliate URLs
 */
function generateSimpleList(actors, filename = 'apify_actors_simple.txt') {
    const sortedActors = actors.sort((a, b) => 
        (a.title || '').localeCompare(b.title || '')
    );
    
    const lines = sortedActors.map(actor => {
        const title = actor.title || actor.name || 'Unknown';
        const affiliateUrl = actor.affiliate_url || actor.url || '';
        return `${title}|${affiliateUrl}`;
    });

    const filePath = path.join(__dirname, '..', filename);
    fs.writeFileSync(filePath, lines.join('\n'), 'utf-8');
    console.log(`Generated simple list: ${filename}`);
}

// Main execution
async function main() {
    console.log('='.repeat(60));
    console.log('Apify Actors Fetcher');
    console.log('='.repeat(60));
    console.log();

    try {
        // Fetch all actors
        const actors = await fetchAllActors(100);

        if (actors.length > 0) {
            // Save to JSON
            saveToJSON(actors, 'apify_actors.json');

            // Generate markdown list
            generateMarkdownList(actors, 'APIFY_ACTORS.md');

            // Generate simple list
            generateSimpleList(actors, 'apify_actors_simple.txt');

            console.log('\n' + '='.repeat(60));
            console.log('Done! All files have been generated.');
            console.log('='.repeat(60));
        } else {
            console.log('No actors were fetched. Please check the API connection.');
        }
    } catch (error) {
        console.error('Fatal error:', error);
        process.exit(1);
    }
}

// Run the script
main();

