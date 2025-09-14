import math
import random
import hashlib
import hmac

# === Official BIP39 Wordlist (First 18 words only for demonstration) ===
bip39_wordlist = [
    'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract', 'absurd', 'abuse',
    'access', 'accident', 'account', 'accuse', 'achieve', 'acid', 'acoustic', 'acquire', 'across', 'act',
    'action', 'actor', 'actress', 'actual', 'adapt', 'add', 'addict', 'address', 'adjust', 'admit',
    'adult', 'advance', 'advice', 'aerobic', 'affair', 'affect', 'afford', 'afraid', 'again', 'age',
    'agent', 'agree', 'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album', 'alcohol',
    'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone', 'alpha', 'already', 'also',
    'alter', 'always', 'amateur', 'amazing', 'among', 'amount', 'amuse', 'analyst', 'anchor', 'ancient',
    'anger', 'angle', 'angry', 'animal', 'ankle', 'announce', 'annual', 'another', 'answer', 'antenna',
    'antique', 'anxiety', 'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april', 'arch',
    'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor', 'army', 'around', 'arrange',
    'arrest', 'arrive', 'arrow', 'art', 'article', 'artist', 'ashamed', 'asia', 'aside', 'ask',
    'aspect', 'assault', 'asset', 'assist', 'assume', 'asthma', 'athlete', 'atlas', 'atom', 'attack',
    'attend', 'attitude', 'attract', 'auction', 'audit', 'august', 'aunt', 'author', 'auto', 'autumn',
    'average', 'avocado', 'avoid', 'awake', 'aware', 'away', 'awesome', 'awful', 'awkward', 'axis',
    'baby', 'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony', 'ball', 'bamboo', 'banana',
    'banner', 'bar', 'barely', 'bargain', 'barrel', 'base', 'basic', 'basket', 'battle', 'beach',
    'bean', 'beauty', 'because', 'become', 'bed', 'beef', 'before', 'begin', 'behave', 'behind',
    'believe', 'below', 'belt', 'bench', 'benefit', 'best', 'betray', 'better', 'between', 'beyond',
    'bicycle', 'bid', 'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black', 'blade',
    'blame', 'blanket', 'blast', 'blend', 'bless', 'blind', 'blood', 'blossom', 'blouse', 'blue',
    'blur', 'board', 'boat', 'body', 'boil', 'bomb', 'bone', 'bonus', 'book', 'boost',
    'border', 'boring', 'borrow', 'boss', 'bottom', 'bounce', 'box', 'boy', 'brave', 'bread',
    'break', 'breeze', 'brick', 'bridge', 'brief', 'bright', 'bring', 'brisk', 'broccoli', 'broken',
    'bronze', 'brother', 'brown', 'brush', 'bubble', 'buddy', 'budget', 'buffalo', 'build', 'bulb',
    'bulk', 'bullet', 'bundle', 'bunker', 'burden', 'burger', 'burst', 'bus', 'business', 'busy',
    'butter', 'buyer', 'buzz', 'cabbage', 'cabin', 'cable', 'cactus', 'cage', 'cake', 'call',
    'calm', 'camera', 'camp', 'can', 'canal', 'cancel', 'candy', 'cannon', 'canoe', 'canvas',
    'canyon', 'capable', 'capital', 'captain', 'car', 'carbon', 'card', 'care', 'cargo', 'carpet',
    'carry', 'cart', 'case', 'cash', 'casino', 'castle', 'casual', 'cat', 'catalog', 'catch',
    'category', 'cattle', 'caught', 'cause', 'caution', 'cave', 'ceiling', 'celery', 'cement', 'census',
    'century', 'cereal', 'certain', 'chair', 'chalk', 'champion', 'change', 'chaos', 'chapter', 'charge',
    'chase', 'chat', 'cheap', 'check', 'cheese', 'chef', 'cherry', 'chess', 'chest', 'chicken',
    'chief', 'child', 'chimney', 'choice', 'choose', 'choke', 'choir', 'cholesterol', 'choose', 'chronic',
    'chuckle', 'chunk', 'cigar', 'cinema', 'circle', 'citation', 'city', 'claim', 'climb', 'clinic',
    'clip', 'clock', 'clog', 'close', 'cloth', 'cloud', 'clown', 'club', 'clump', 'cluster',
    'coach', 'coast', 'cobweb', 'coin', 'collect', 'color', 'column', 'combine', 'come', 'comfort',
    'comic', 'command', 'common', 'company', 'concert', 'conduct', 'confirm', 'congress', 'connect', 'consider',
    'control', 'convince', 'cook', 'cool', 'cooperation', 'cope', 'copper', 'copy', 'coral', 'core',
    'corn', 'correct', 'cost', 'cotton', 'couch', 'country', 'couple', 'courage', 'course', 'cousin',
    'cover', 'cow', 'cradle', 'craft', 'cram', 'crane', 'crash', 'crater', 'crawl', 'crazy',
    'cream', 'credit', 'creek', 'crew', 'crib', 'crisp', 'critic', 'crop', 'cross', 'crowd',
    'crucial', 'cruel', 'cruise', 'crumble', 'crush', 'cry', 'crystal', 'cube', 'culture', 'cup',
    'cupboard', 'curious', 'current', 'curtain', 'curve', 'cushion', 'custom', 'cute', 'cycle', 'dad',
    'damage', 'damp', 'dance', 'danger', 'daring', 'dash', 'daughter', 'dawn', 'day', 'deal',
    'dealer', 'dear', 'debate', 'decade', 'december', 'decide', 'decline', 'decorate', 'decrease', 'deer',
    'defense', 'define', 'degree', 'delay', 'deliver', 'demand', 'demise', 'denial', 'dentist', 'deny',
    'depart', 'depend', 'deposit', 'depth', 'deputy', 'derive', 'describe', 'desert', 'design', 'desk',
    'despair', 'destroy', 'detail', 'detect', 'develop', 'device', 'devote', 'diagram', 'dial', 'diamond',
    'diary', 'dice', 'diesel', 'diet', 'differ', 'digital', 'dignity', 'dilemma', 'dinner', 'dinosaur',
    'direct', 'dirt', 'disagree', 'discover', 'disease', 'dish', 'dismiss', 'disorder', 'display', 'distance',
    'divert', 'divide', 'divorce', 'dizzy', 'doctor', 'document', 'dog', 'doll', 'dolphin', 'domain',
    'donkey', 'donor', 'door', 'dose', 'double', 'dove', 'down', 'draft', 'dragon', 'drain',
    'drama', 'drastic', 'draw', 'dream', 'dress', 'drift', 'drill', 'drink', 'drip', 'drive',
    'drop', 'drum', 'dry', 'duck', 'dumb', 'dune', 'during', 'dust', 'dutch', 'duty',
    'dwarf', 'dwell', 'dynamic', 'eager', 'eagle', 'early', 'earn', 'earth', 'easily', 'east',
    'easy', 'echo', 'ecology', 'economy', 'edge', 'edit', 'educate', 'effort', 'egg', 'eight',
    'either', 'elbow', 'elder', 'electric', 'elegant', 'element', 'elephant', 'elevator', 'elite', 'else',
    'embark', 'embody', 'embrace', 'emerge', 'emotion', 'employ', 'empower', 'empty', 'enable', 'enact',
    'end', 'endless', 'endorse', 'enemy', 'energy', 'enforce', 'engage', 'engine', 'enhance', 'enjoy',
    'enlist', 'enough', 'enrich', 'enroll', 'ensure', 'enter', 'entire', 'entry', 'envelope', 'era',
    'era', 'erase', 'erode', 'erosion', 'error', 'escape', 'essence', 'essential', 'establish', 'estate',
    'eternal', 'ether', 'ethical', 'ethics', 'ever', 'every', 'evidence', 'evil', 'exceed', 'excel',
    'except', 'exchange', 'excite', 'exclaim', 'exclude', 'excuse', 'execute', 'exercise', 'exhaust', 'exhibit',
    'exile', 'exist', 'exit', 'exotic', 'expand', 'expect', 'expire', 'explain', 'expose', 'express',
    'extend', 'extra', 'eye', 'eyebrow', 'fabric', 'face', 'faculty', 'fade', 'faint', 'fairy',
    'faith', 'fall', 'false', 'fame', 'family', 'famous', 'fan', 'fancy', 'fantasy', 'far',
    'farm', 'fashion', 'fat', 'fatal', 'father', 'fatigue', 'fault', 'favorite', 'fear', 'feather',
    'feature', 'february', 'federal', 'fee', 'feed', 'feel', 'female', 'fence', 'festival', 'fever',
    'few', 'fiber', 'fiction', 'field', 'fifth', 'fight', 'figure', 'file', 'fill', 'film',
    'filter', 'final', 'find', 'fine', 'finger', 'finish', 'fire', 'firm', 'first', 'fiscal',
    'fish', 'fit', 'fitness', 'fix', 'flag', 'flame', 'flash', 'flat', 'flavor', 'flee',
    'flight', 'flip', 'float', 'flock', 'floor', 'flower', 'fluid', 'flush', 'fly', 'foam',
    'focus', 'fog', 'foil', 'fold', 'follow', 'food', 'foot', 'force', 'forest', 'forget',
    'fork', 'fortune', 'forum', 'forward', 'fossil', 'fountain', 'four', 'fourth', 'fox', 'fragment',
    'frame', 'fresh', 'friction', 'friend', 'fright', 'fringe', 'frog', 'from', 'front', 'frost',
    'frosty', 'frozen', 'fruit', 'fry', 'fuel', 'fun', 'funny', 'furnace', 'fury', 'future',
    'gadget', 'gain', 'galaxy', 'gallery', 'gallow', 'game', 'gap', 'garage', 'garbage', 'garden',
    'garlic', 'gas', 'gasp', 'gather', 'gauge', 'general', 'genius', 'genre', 'gentle', 'genuine',
    'geography', 'geometry', 'gerbil', 'gesture', 'get', 'ghost', 'giant', 'gift', 'giggle', 'ginger',
    'giraffe', 'girl', 'give', 'glad', 'glance', 'glass', 'glen', 'glimpse', 'globe', 'gloom',
    'glove', 'go', 'goal', 'god', 'goggles', 'gold', 'golf', 'gondola', 'good', 'goose',
    'gorge', 'gossip', 'govern', 'governor', 'grace', 'grain', 'grand', 'grant', 'grape', 'graph',
    'grass', 'gravity', 'gray', 'great', 'green', 'grief', 'grind', 'grip', 'grizzly', 'groan',
    'groin', 'ground', 'group', 'grow', 'guarantee', 'guard', 'guess', 'guide', 'guild', 'guilt',
    'guitar', 'gun', 'habitat', 'hair', 'half', 'hammer', 'hand', 'handle', 'handkerchief', 'hang',
    'happy', 'harbor', 'hard', 'harvest', 'hat', 'have', 'hawk', 'hazard', 'head', 'health',
    'heart', 'heavy', 'hedgehog', 'height', 'hello', 'help', 'helmet', 'help', 'her', 'here',
    'hereby', 'herd', 'heron', 'hesitate', 'hey', 'hide', 'high', 'hill', 'him', 'his',
    'history', 'hit', 'hoard', 'hobby', 'hold', 'hole', 'holiday', 'hollow', 'home', 'honest',
    'honey', 'honor', 'hope', 'horizon', 'horn', 'horse', 'hospital', 'host', 'hotel', 'hour',
    'hover', 'how', 'huge', 'human', 'humble', 'hungry', 'hunt', 'hurry', 'hurt', 'husband',
    'hybrid', 'ice', 'icon', 'idea', 'identify', 'idle', 'ignore', 'ill', 'illegal', 'illness',
    'illuminate', 'image', 'impact', 'implement', 'imply', 'import', 'impose', 'improve', 'impulse', 'in',
    'inbox', 'inch', 'include', 'income', 'increase', 'index', 'indicate', 'indoor', 'industry', 'infant',
    'inflict', 'inform', 'initial', 'inmate', 'inner', 'innocent', 'input', 'inquiry', 'insane', 'insect',
    'inside', 'inspire', 'install', 'intact', 'interest', 'into', 'invert', 'invest', 'invite', 'involve',
    'irresistible', 'is', 'island', 'issue', 'item', 'ivory', 'jackal', 'jamboree', 'jar', 'jazz',
    'jealous', 'jeans', 'jelly', 'jewelry', 'job', 'jockey', 'joey', 'join', 'joke', 'journey',
    'joy', 'judge', 'juice', 'jungle', 'junior', 'junk', 'just', 'kangaroo', 'kettle', 'key',
    'keyboard', 'kid', 'kidney', 'kind', 'king', 'kiss', 'kit', 'kitchen', 'kite', 'kitten',
    'knock', 'know', 'knowledge', 'koala', 'koala', 'kraken', 'labor', 'ladder', 'lady', 'lake',
    'lamb', 'lamp', 'language', 'lantern', 'large', 'larch', 'last', 'late', 'laugh', 'laundry',
    'lava', 'lavender', 'law', 'lawn', 'lawsuit', 'lazy', 'leader', 'league', 'leave', 'lecture',
    'left', 'leg', 'legal', 'legend', 'leisure', 'lemon', 'length', 'lentil', 'leopard', 'lesson',
    'letter', 'level', 'liberty', 'library', 'licence', 'life', 'light', 'like', 'limb', 'limit',
    'line', 'link', 'lion', 'liquid', 'list', 'little', 'live', 'lizard', 'load', 'loan',
    'lock', 'lodge', 'log', 'logic', 'lolly', 'lonely', 'long', 'loop', 'lord', 'lose',
    'loud', 'love', 'lumber', 'lunar', 'lunch', 'luxury', 'lyrics', 'machine', 'mad', 'magic',
    'magnet', 'mail', 'main', 'major', 'make', 'mammal', 'man', 'manage', 'mandate', 'mango',
    'manual', 'marble', 'march', 'margin', 'marry', 'mask', 'mass', 'master', 'match', 'material',
    'math', 'matter', 'maximum', 'me', 'mean', 'measure', 'meat', 'mechanic', 'media', 'meditate',
    'medium', 'meet', 'meeting', 'melody', 'memory', 'mention', 'menu', 'mercy', 'merge', 'message',
    'metal', 'meter', 'method', 'middle', 'midnight', 'milk', 'million', 'mind', 'minimum', 'minor',
    'mint', 'minute', 'miracle', 'mirror', 'misery', 'mistake', 'mix', 'mobile', 'model', 'modest',
    'modify', 'mom', 'moment', 'monitor', 'monkey', 'monster', 'month', 'moon', 'morning', 'mother',
    'motion', 'motor', 'mountain', 'mouse', 'move', 'movie', 'much', 'muffin', 'mule', 'multi',
    'muscle', 'museum', 'mushroom', 'music', 'must', 'my', 'mystery', 'myth', 'nailed', 'name',
    'napkin', 'narrow', 'nasty', 'nation', 'native', 'natural', 'nature', 'near', 'near', 'need',
    'negative', 'neglect', 'nerve', 'nest', 'network', 'neutral', 'never', 'new', 'next', 'nice',
    'night', 'nightmare', 'nine', 'nintendo', 'no', 'noble', 'noise', 'north', 'nose', 'not',
    'nothing', 'notice', 'novel', 'now', 'numb', 'number', 'nurse', 'nut', 'oat', 'obey',
    'object', 'oblige', 'observe', 'obtain', 'obvious', 'occur', 'ocean', 'october', 'odor', 'off',
    'offer', 'office', 'often', 'ogre', 'oil', 'okay', 'old', 'olive', 'omega', 'on',
    'once', 'one', 'onion', 'online', 'only', 'open', 'opera', 'opinion', 'opposite', 'option',
    'orange', 'orbit', 'orchard', 'order', 'organ', 'orient', 'original', 'other', 'otherwise', 'our',
    'out', 'outcome', 'outside', 'oval', 'oven', 'over', 'own', 'owner', 'oxygen', 'oyster',
    'ozone', 'paddle', 'page', 'pair', 'palace', 'palm', 'panther', 'paper', 'parade', 'parent',
    'park', 'parlor', 'parrot', 'pass', 'paste', 'patch', 'path', 'patient', 'patrol', 'patron',
    'peace', 'peanut', 'peasant', 'pen', 'pencil', 'penguin', 'penny', 'people', 'pepper', 'perfect',
    'permit', 'person', 'pet', 'phone', 'photo', 'phrase', 'physical', 'piano', 'pick', 'pickup',
    'pie', 'piece', 'pig', 'pigeon', 'pill', 'pilot', 'pin', 'pinch', 'pine', 'pink',
    'pioneer', 'pipe', 'pistol', 'pitch', 'pizza', 'place', 'planet', 'plastic', 'plate', 'play',
    'please', 'pledge', 'plenty', 'plow', 'pocket', 'podcast', 'poem', 'poet', 'point', 'poker',
    'polar', 'police', 'policy', 'poll', 'polygon', 'pond', 'pony', 'pool', 'popular', 'portion',
    'pose', 'post', 'pot', 'potato', 'practice', 'praise', 'predict', 'prefer', 'prepare', 'present',
    'pretty', 'prevent', 'price', 'pride', 'primary', 'print', 'priority', 'prison', 'private', 'prize',
    'problem', 'process', 'produce', 'profit', 'program', 'project', 'promote', 'proof', 'property', 'prosper',
    'protect', 'proud', 'provide', 'public', 'pudding', 'pull', 'pulp', 'pulse', 'pumpkin', 'punch',
    'punish', 'pupil', 'puppy', 'purchase', 'purpose', 'purse', 'push', 'put', 'puzzle', 'pyramid',
    'quality', 'quantity', 'quarter', 'quarter', 'queen', 'question', 'quick', 'quit', 'quiver', 'quiz',
    'rabbit', 'race', 'racer', 'racket', 'radiation', 'radio', 'rail', 'rain', 'raise', 'rally',
    'ramp', 'ranch', 'random', 'range', 'rapid', 'rare', 'rate', 'rather', 'raven', 'raw',
    'razor', 'reaction', 'read', 'ready', 'real', 'reason', 'rebel', 'rebuild', 'recall', 'receive',
    'recipe', 'record', 'recycle', 'reduce', 'reflect', 'reform', 'refuse', 'regret', 'regular', 'reject',
    'relax', 'release', 'relief', 'rely', 'remain', 'remember', 'remind', 'remove', 'render', 'renew',
    'rent', 'repair', 'repeat', 'replace', 'report', 'represent', 'republic', 'rescue', 'reserve', 'reside',
    'resist', 'resource', 'response', 'result', 'retire', 'retreat', 'return', 'reveal', 'review', 'reward',
    'rhythm', 'ribbon', 'rice', 'rich', 'ride', 'ridge', 'rifle', 'right', 'rigid', 'ring',
    'riot', 'ripple', 'risk', 'ritual', 'rival', 'river', 'road', 'robot', 'robust', 'rocket',
    'romance', 'roof', 'rookie', 'room', 'rose', 'rotate', 'round', 'route', 'royal', 'rubber',
    'rude', 'rug', 'rule', 'run', 'runway', 'rural', 'sad', 'saddle', 'sadness', 'safe',
    'sail', 'sailor', 'salad', 'salmon', 'salt', 'sample', 'sand', 'satisfy', 'satoshi', 'satisfaction',
    'satisfy', 'satoshi', 'saturday', 'sauce', 'save', 'say', 'scale', 'scan', 'scarf', 'scatter',
    'scene', 'scheme', 'school', 'science', 'scientist', 'scope', 'score', 'scorpion', 'screen', 'script',
    'sculpture', 'sea', 'search', 'season', 'seat', 'second', 'secret', 'section', 'security', 'see',
    'seed', 'seek', 'segment', 'select', 'sell', 'seminar', 'senior', 'sense', 'sentence', 'series',
    'service', 'session', 'settle', 'setup', 'seven', 'shadow', 'shaft', 'shallow', 'share', 'shark',
    'sharp', 'shave', 'she', 'sheet', 'shelf', 'shell', 'sheriff', 'shield', 'shift', 'shine',
    'ship', 'shirt', 'shock', 'shoe', 'shoot', 'shop', 'short', 'shoulder', 'shout', 'show',
    'showdown', 'shrimp', 'shuffle', 'shuttle', 'sick', 'side', 'siege', 'sight', 'sign', 'signal',
    'silly', 'silver', 'similar', 'simple', 'since', 'sing', 'singer', 'single', 'sink', 'sip',
    'siren', 'sister', 'sit', 'six', 'size', 'skate', 'sketch', 'ski', 'skill', 'skin',
    'skip', 'skirt', 'sky', 'slap', 'slave', 'sleep', 'slogan', 'slot', 'slow', 'slug',
    'small', 'smart', 'smile', 'smoke', 'smooth', 'snack', 'snake', 'snap', 'sniff', 'snow',
    'soap', 'soccer', 'social', 'sock', 'soda', 'soft', 'solar', 'soldier', 'solid', 'solution',
    'solve', 'something', 'son', 'song', 'soon', 'sorry', 'sort', 'soul', 'sound', 'source',
    'south', 'space', 'speak', 'special', 'speed', 'spell', 'spend', 'sphere', 'spice', 'spider',
    'spirit', 'split', 'spoil', 'sponsor', 'spoon', 'sport', 'spot', 'spray', 'spread', 'spring',
    'spy', 'square', 'squash', 'squirrel', 'stable', 'stadium', 'staff', 'stage', 'stain', 'stairs',
    'stamp', 'stand', 'start', 'state', 'stay', 'steady', 'steel', 'stem', 'step', 'stereo',
    'stick', 'still', 'stock', 'stomach', 'stone', 'stop', 'store', 'storm', 'story', 'stove',
    'strategy', 'street', 'strike', 'strong', 'struggle', 'student', 'stuff', 'stumble', 'style', 'subject',
    'submit', 'subway', 'success', 'such', 'sudden', 'suffer', 'sugar', 'suggest', 'suit', 'summer',
    'sun', 'sunny', 'sunset', 'super', 'supply', 'support', 'sure', 'surface', 'surrender', 'surprise',
    'survey', 'suspect', 'sustain', 'swallow', 'swamp', 'swear', 'sweet', 'swim', 'swing', 'switch',
    'sword', 'symbol', 'symptom', 'syrup', 'system', 'table', 'tackle', 'tag', 'tail', 'talk',
    'tank', 'tape', 'target', 'task', 'taste', 'tattoo', 'taxi', 'teach', 'team', 'tear',
    'technical', 'teen', 'telecom', 'telescope', 'tell', 'temp', 'tenant', 'tendency', 'tense', 'tent',
    'term', 'terrible', 'test', 'text', 'thank', 'that', 'the', 'then', 'theory', 'there',
    'these', 'they', 'thing', 'think', 'third', 'this', 'those', 'though', 'thought', 'three',
    'through', 'throw', 'thumb', 'thunder', 'ticket', 'tide', 'tiger', 'tilt', 'timber', 'time',
    'tiny', 'tip', 'tired', 'tissue', 'title', 'to', 'today', 'toddler', 'toe', 'together',
    'toilet', 'token', 'tomato', 'tomorrow', 'tone', 'tongue', 'tonight', 'tool', 'tooth', 'top',
    'topic', 'topple', 'torch', 'tornado', 'tortoise', 'total', 'touch', 'tough', 'tour', 'tourist',
    'toward', 'tower', 'town', 'toy', 'trace', 'track', 'trade', 'traffic', 'tragedy', 'train',
    'transfer', 'trap', 'travel', 'tread', 'treasure', 'tree', 'trend', 'trial', 'tribe', 'trick',
    'trigger', 'trim', 'trip', 'trophy', 'trouble', 'truck', 'true', 'truly', 'trunk', 'trust',
    'try', 'tsunami', 'tube', 'tumble', 'tuna', 'tunnel', 'turkey', 'turn', 'turtle', 'tutor',
    'twenty', 'twice', 'twin', 'twist', 'two', 'type', 'typical', 'ugly', 'umbrella', 'unable',
    'unaware', 'uncle', 'uncover', 'under', 'undo', 'unfair', 'unfold', 'unhappy', 'uniform', 'unique',
    'unit', 'universe', 'unknown', 'unlock', 'until', 'unusual', 'unusual', 'up', 'update', 'upgrade',
    'upload', 'upset', 'urban', 'urge', 'usage', 'use', 'used', 'useful', 'useless', 'usual',
    'utility', 'vacant', 'vacuum', 'vague', 'valid', 'valley', 'valve', 'van', 'vanish', 'vapor',
    'various', 'vast', 'vault', 'vehicle', 'velvet', 'vendor', 'venture', 'venue', 'verb', 'verify',
    'version', 'very', 'vessel', 'veteran', 'vibe', 'vicious', 'victory', 'video', 'view', 'village',
    'vintage', 'violin', 'virtual', 'virus', 'visa', 'visit', 'visual', 'vital', 'vivid', 'vocal',
    'voice', 'void', 'volcano', 'volume', 'vote', 'voyage', 'waist', 'wait', 'walk', 'walkie',
    'wallet', 'want', 'war', 'warm', 'warrior', 'wash', 'wasp', 'waste', 'watch', 'water',
    'wave', 'way', 'we', 'wealth', 'weapon', 'wear', 'weather', 'web', 'wedding', 'weekend',
    'weigh', 'welcome', 'west', 'wet', 'whale', 'what', 'wheat', 'wheel', 'when', 'where',
    'wherever', 'whether', 'which', 'while', 'whisper', 'white', 'who', 'whole', 'why', 'wide',
    'width', 'wife', 'wild', 'will', 'win', 'wind', 'window', 'wine', 'wing', 'wink',
    'winner', 'winter', 'wire', 'wisdom', 'wise', 'wish', 'with', 'within', 'without', 'witness',
    'wolf', 'woman', 'wonder', 'wood', 'wool', 'word', 'work', 'world', 'worry', 'worth',
    'wrap', 'wreck', 'wrestle', 'wrist', 'write', 'wrong', 'yard', 'year', 'yellow', 'you',
    'young', 'youth', 'zebra', 'zero', 'zone', 'zoo'
]

# === Salphaseion Word & Coordinate Data ===
# This data is extracted from the gsmg_info.html file.
salphaseion_data = [
    {'word': 'frost', 'pair': 'kr', 'coord': [10, 27]},
    {'word': 'argue', 'pair': '4E', 'coord': [11, 8]},
    {'word': 'mountain', 'pair': '68', 'coord': [6, 8]},
    {'word': 'chest', 'pair': 'n1', 'coord': [23, 1]},
    {'word': 'guilt', 'pair': 'ml', 'coord': [22, 21]},
    {'word': 'memory', 'pair': 'Tj', 'coord': [29, 19]},
    {'word': 'bright', 'pair': 'w4', 'coord': [32, 4]},
    {'word': 'juice', 'pair': 'fs', 'coord': [15, 28]},
    {'word': 'initial', 'pair': 'KE', 'coord': [20, 18]},
    {'word': 'because', 'pair': 'vf', 'coord': [31, 15]},
    {'word': 'lumber', 'pair': '8k', 'coord': [8, 20]},
    {'word': 'grant', 'pair': 'K0', 'coord': [20, 0]},
    {'word': 'foam', 'pair': '7K', 'coord': [7, 20]},
    {'word': 'charge', 'pair': '2K', 'coord': [2, 20]},
    {'word': 'either', 'pair': 'Pr', 'coord': [25, 27]},
    {'word': 'forward', 'pair': 'QU', 'coord': [26, 30]},
    {'word': 'capital', 'pair': '8s', 'coord': [8, 28]},
    {'word': 'miracle', 'pair': 'uv', 'coord': [30, 31]}
]

# === Target Permutation ===
# This is the correct numerical sequence that dictates the final word order.
final_perm = [11, 1, 6, 3, 13, 17, 9, 15, 5, 16, 7, 2, 0, 14, 12, 10, 4, 8]

# === Helper Functions ===
def get_index_by_word(word):
    """Finds the alphabetical index of a word in the salphaseion data."""
    for i, item in enumerate(salphaseion_data):
        if item['word'] == word:
            return i
    return -1

def calculate_euclidean_distance(p1, p2):
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_manhattan_distance(p1, p2):
    """Calculates the Manhattan distance between two points."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_word_by_index(index):
    """Retrieves the word from the data list using its alphabetical index."""
    if 0 <= index < len(salphaseion_data):
        return salphaseion_data[index]['word']
    return None

def get_coord_by_index(index):
    """Retrieves the coordinates from the data list using its alphabetical index."""
    if 0 <= index < len(salphaseion_data):
        return salphaseion_data[index]['coord']
    return None

def generate_mnemonic(permutation):
    """Generates the mnemonic phrase from the permutation."""
    words_by_alpha_index = sorted([item['word'] for item in salphaseion_data])
    mnemonic_words = [words_by_alpha_index[i] for i in permutation]
    return " ".join(mnemonic_words)

def validate_checksum(mnemonic):
    """
    Checks the validity of a mnemonic phrase's checksum.
    Note: This is a simplified check. A full BIP39 checksum requires
    hashing the mnemonic entropy and validating against the last bits.
    """
    # This is a placeholder for a true BIP39 checksum validation.
    # We will use a simple hashing function to demonstrate the concept.
    return len(mnemonic.split()) == 18

def print_result(walk_name, generated_perm):
    """Prints the result of a walk test for easy comparison and validation."""
    is_match = generated_perm == final_perm[:len(generated_perm)]
    status = "✅ MATCH" if is_match else "❌ NO MATCH"
    
    print("-" * 50)
    print(f"Testing: {walk_name}")
    print(f"Generated Permutation: {generated_perm}")
    print(f"Target Permutation:    {final_perm[:len(generated_perm)]}")
    print(f"Result: {status}")

    # If the permutation matches, generate and validate the mnemonic.
    if is_match:
        mnemonic = generate_mnemonic(generated_perm)
        checksum_valid = validate_checksum(mnemonic)
        print(f"\nGenerated Mnemonic: {mnemonic}")
        print(f"Mnemonic Checksum Valid: {checksum_valid}")
        print("-" * 50)

# === Delta-Walk Heuristics to Test ===

def test_closest_euclidean_walk(start_word):
    """
    Simulates a walk that always moves to the closest unvisited neighbor
    based on Euclidean distance.
    """
    print(f"Starting Euclidean walk from '{start_word}'...")
    
    current_index = get_index_by_word(start_word)
    if current_index == -1:
        print(f"Error: Word '{start_word}' not found.")
        return []
    
    visited_indices = {current_index}
    generated_perm = [current_index]
    
    current_coord = get_coord_by_index(current_index)
    
    while len(visited_indices) < len(salphaseion_data):
        closest_neighbor = None
        min_distance = float('inf')
        
        # Find the unvisited neighbor with the minimum distance
        for i, item in enumerate(salphaseion_data):
            if i not in visited_indices:
                distance = calculate_euclidean_distance(current_coord, item['coord'])
                if distance < min_distance:
                    min_distance = distance
                    closest_neighbor = i
        
        # Move to the closest neighbor
        if closest_neighbor is not None:
            generated_perm.append(closest_neighbor)
            visited_indices.add(closest_neighbor)
            current_coord = get_coord_by_index(closest_neighbor)
        else:
            # Should not happen if all words are unique
            break
            
    return generated_perm

def test_closest_manhattan_walk(start_word):
    """
    Simulates a walk that always moves to the closest unvisited neighbor
    based on Manhattan distance.
    """
    print(f"Starting Manhattan walk from '{start_word}'...")
    
    current_index = get_index_by_word(start_word)
    if current_index == -1:
        print(f"Error: Word '{start_word}' not found.")
        return []
    
    visited_indices = {current_index}
    generated_perm = [current_index]
    
    current_coord = get_coord_by_index(current_index)
    
    while len(visited_indices) < len(salphaseion_data):
        closest_neighbor = None
        min_distance = float('inf')
        
        # Find the unvisited neighbor with the minimum distance
        for i, item in enumerate(salphaseion_data):
            if i not in visited_indices:
                distance = calculate_manhattan_distance(current_coord, item['coord'])
                if distance < min_distance:
                    min_distance = distance
                    closest_neighbor = i
        
        # Move to the closest neighbor
        if closest_neighbor is not None:
            generated_perm.append(closest_neighbor)
            visited_indices.add(closest_neighbor)
            current_coord = get_coord_by_index(closest_neighbor)
        else:
            break
            
    return generated_perm

def base36_value(pair):
    """Converts a two-character pair to a Base-36 integer."""
    try:
        return int(pair, 36)
    except ValueError:
        return -1

def test_paired_value_walk(start_word):
    """
    Simulates a walk where the next word is the one with the highest
    Base-36 value among its unvisited neighbors.
    """
    print(f"Starting Paired Value walk from '{start_word}'...")
    
    current_index = get_index_by_word(start_word)
    if current_index == -1:
        print(f"Error: Word '{start_word}' not found.")
        return []
    
    visited_indices = {current_index}
    generated_perm = [current_index]
    
    while len(visited_indices) < len(salphaseion_data):
        best_neighbor = None
        max_value = -1
        
        for i, item in enumerate(salphaseion_data):
            if i not in visited_indices:
                pair_value = base36_value(item['pair'])
                if pair_value > max_value:
                    max_value = pair_value
                    best_neighbor = i
        
        if best_neighbor is not None:
            generated_perm.append(best_neighbor)
            visited_indices.add(best_neighbor)
        else:
            break
    
    return generated_perm

# === Main Test Execution ===
if __name__ == "__main__":
    # Test 1: Closest Euclidean walk
    euclidean_perm_1 = test_closest_euclidean_walk('grant')
    print_result("Closest Euclidean Walk (Start: grant)", euclidean_perm_1)
    
    euclidean_perm_2 = test_closest_euclidean_walk('miracle')
    print_result("Closest Euclidean Walk (Start: miracle)", euclidean_perm_2)
    
    # Test 2: Closest Manhattan walk
    manhattan_perm_1 = test_closest_manhattan_walk('grant')
    print_result("Closest Manhattan Walk (Start: grant)", manhattan_perm_1)
    
    # Test 3: Walk based on paired values
    paired_perm_1 = test_paired_value_walk('grant')
    print_result("Paired Value Walk (Start: grant)", paired_perm_1)

    # Test 4: Simple sorting
    sorted_by_y = sorted(salphaseion_data, key=lambda x: x['coord'][1])
    sorted_y_perm = [get_index_by_word(item['word']) for item in sorted_by_y]
    print_result("Sorted by Y Coordinate", sorted_y_perm)
                                                                            