<?php
// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);
// error_reporting(E_ALL);
$proj_root = dirname(dirname(dirname(__DIR__)));

function is_valid_bundle($bundle_id) {
	# check valid bundle id, same regex as in `common_lib.py`
	return preg_match('/^[A-Za-z0-9\.\-]{1,155}$/', $bundle_id);
}

function normalize_bundle($bundle_id) {
	$valid = is_valid_bundle($bundle_id);
	return [$valid ? $bundle_id : '_manually', $valid];
}

function path_for($parts) { return implode(DIRECTORY_SEPARATOR, $parts); }

function mark_needs_update($norm_bundle) {
	global $proj_root;
	$pth = path_for([$proj_root, 'data', '_in']);
	@mkdir($pth, 0755, true);
	file_put_contents(path_for([$pth, 'in_'.$norm_bundle]), '.');
}

function random_filename($norm_bundle) {
	global $proj_root;
	$dir = path_for(array_merge([$proj_root, 'data'], explode('.', $norm_bundle)));
	@mkdir($dir, 0755, true);
	do {
		$key = '';
		$keys = array_merge(range(0, 9), range('a', 'z'));
		for ($i = 0; $i < 48; $i++) {
			$key .= $keys[array_rand($keys)];
		}
		$full = path_for([$dir, "id_$key.json"]);
	} while (file_exists($full));
	return [$full, $key];
}

// Generate response

function make_output($msg, $url=null, $when=null, $key=null) {
	$obj = [ 'v' => 1, 'status' => $msg ];
	if ($url) {
		$obj['url'] = $url;
		if ($when) {
			$obj['when'] = $when;  # date('Y-m-d H:i:s', )
		}
	}
	if ($key) { $obj['key'] = $key; }
	echo json_encode($obj);
}

function response_success($bundle_id, $key) {
	$url = $bundle_id ? 'https://appchk.de/app/'.$bundle_id.'/index.html' : null;
	# next update will be in ... X seconds (up to 1 min)
	make_output('ok', $url, ceil(time()/120)*120 - time(), $key);
}

function response_fail($error) {
	http_response_code(400);
	make_output($error);
}

// MAIN

$err = null;
$content = file_get_contents('php://input');
// OR: disable json check and store file immediately?
$json = json_decode($content);
if ($json->v == 1
	&& $json->duration > 0
	&& !is_null($json->{'app-bundle'})
	&& !is_null($json->logs))
{
	[$bundle_id, $valid] = normalize_bundle($json->{'app-bundle'});
	[$filename, $key] = random_filename($bundle_id);
	$fp = @fopen($filename, 'w');
	if ($fp) {
		@fwrite($fp, $content);
		@fclose($fp);
		mark_needs_update($bundle_id);
	} else {
		$err = 'could not save.';
	}
} else {
	$err = 'wrong json format.';
}

if ($err) {
	response_fail($err);
} else {
	response_success($valid ? $bundle_id : null, $key);
}
?>
