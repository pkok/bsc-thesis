function clearall() { cld();clf();clc(); }
clearall();

batch generate_model();
batch generate_distances();
batch generate_constraints();
batch fabrik(chain_nr, chain_size, target);
function draw_line(p1, p2);
function pt(x);
function wavg(w1, p1, w2, p2);
function distance(x, y);

// Define the chain names
add_const(HEAD = 0);
add_const(HEAD_SIZE = 3);
add_const(LEFT = 1);
add_const(LEFT_SIZE = 5);
add_const(RIGHT = 2);
add_const(RIGHT_SIZE = 5);

add_const(CENTER = 0);
add_const(NECK = 1);
add_const(LASER = 2);

add_const(SHOULDER = 1);
add_const(ELBOW = 2);
add_const(WRIST = 3);
add_const(HAND = 4);

add_const(ROLL = 0);
add_const(PITCH = 1);
add_const(YAW = 2);

add_const(MIN = 0);
add_const(MAX = 1);
add_const(CURRENT = 2);

// Define the link structure
add_const(offset_scale = 0.05);
add_const(NeckOffsetZ = 126.50);
add_const(LaserOffsetZ = 106.60);
add_const(ShoulderOffsetY = 98);
add_const(ShoulderOffsetZ = 100);
add_const(UpperArmLength = 90);
add_const(LowerArmLength = 50.55);
add_const(HandOffsetX = 58);
add_const(HandOffsetZ = -15.90);

batch initialize() {
  cprint("Initializing...");
  cprint("Generating the robot model...");
  generate_model();
  cprint("Computing the distances between joints");
  generate_distances();
  cprint("Setting the orientational and rotational constraints");
  generate_constraints();
  //generate_targets();
  TOLERANCE = 0.05;

  point[HEAD][LASER] = cyan(c3ga_point(KChain[HEAD][LASER])),
  point[LEFT][HAND] = cyan(c3ga_point(KChain[LEFT][HAND])),
  point[RIGHT][HAND] = cyan(c3ga_point(KChain[RIGHT][HAND])),
  dynamic {
    _somevar_H = fabrik(HEAD, HEAD_SIZE, (e3ga) point[HEAD][LASER]);
  }
  dynamic {
    _somevar_L = fabrik(LEFT, LEFT_SIZE, (e3ga) point[LEFT][HAND]);
  }
  dynamic {
    _somevar_R = fabrik(RIGHT, RIGHT_SIZE, (e3ga) point[RIGHT][HAND]);
  };
  cprint("Ready to run FABRIK...");
}


batch generate_model() {
  // Define and draw the body points
  KChain[HEAD][CENTER] = (e3ga) 0;
  KChain[HEAD][NECK] = pt(offset_scale * NeckOffsetZ * e3);
  KChain[HEAD][LASER] = pt(offset_scale * (NeckOffsetZ + LaserOffsetZ) * e3);

  KChain[LEFT][CENTER] = (e3ga) 0;
  KChain[LEFT][SHOULDER] = pt(offset_scale * (ShoulderOffsetZ * e3 - ShoulderOffsetY * e2));
  KChain[LEFT][ELBOW] = pt(offset_scale * (ShoulderOffsetZ * e3 - ShoulderOffsetY * e2 + UpperArmLength * e1));
  KChain[LEFT][WRIST] = pt(offset_scale * (ShoulderOffsetZ * e3 - ShoulderOffsetY * e2 + (UpperArmLength + LowerArmLength) * e1));
  KChain[LEFT][HAND] = pt(offset_scale * ((ShoulderOffsetZ + HandOffsetZ) * e3 - ShoulderOffsetY * e2 + (UpperArmLength + LowerArmLength + HandOffsetX) * e1));

  KChain[RIGHT][CENTER] = (e3ga) 0;
  KChain[RIGHT][SHOULDER] = pt(offset_scale * (ShoulderOffsetZ * e3 + ShoulderOffsetY * e2));
  KChain[RIGHT][ELBOW] = pt(offset_scale * (ShoulderOffsetZ * e3 + ShoulderOffsetY * e2 + UpperArmLength * e1));
  KChain[RIGHT][WRIST] = pt(offset_scale * (ShoulderOffsetZ * e3 + ShoulderOffsetY * e2 + (UpperArmLength + LowerArmLength) * e1));
  KChain[RIGHT][HAND] = pt(offset_scale * ((ShoulderOffsetZ + HandOffsetZ) * e3 + ShoulderOffsetY * e2 + (UpperArmLength + LowerArmLength + HandOffsetX) * e1));

  // Draw the lines between the joints
  dynamic{
  for (i = 0; i < HEAD_SIZE - 1; i = i + 1) {
    link[HEAD][i] = draw_line(KChain[HEAD][i], KChain[HEAD][i + 1]),
  }
  for (i = 0; i < LEFT_SIZE - 1; i = i + 1) {
    link[LEFT][i] = draw_line(KChain[LEFT][i], KChain[LEFT][i + 1]),
  }
  for (i = 0; i < RIGHT_SIZE - 1; i = i + 1) {
    link[RIGHT][i] = draw_line(KChain[RIGHT][i], KChain[RIGHT][i + 1]),
  }
  };

  // Draw the joint poisitions
  dynamic {
    point[HEAD][CENTER] = black(c3ga_point(KChain[HEAD][CENTER])),
    point[HEAD][NECK] = yellow(c3ga_point(KChain[HEAD][NECK])),

    for (i = LEFT; i <= RIGHT; i = i + 1) {
      point[i][CENTER] = black(c3ga_point(KChain[i][CENTER])),
      point[i][SHOULDER] = yellow(c3ga_point(KChain[i][SHOULDER])),
      point[i][ELBOW] = red(c3ga_point(KChain[i][ELBOW])),
      point[i][WRIST] = green(c3ga_point(KChain[i][WRIST])),
    }
  };
}


batch generate_constraints() {
  rad = pi / 180;
  rot[HEAD][CENTER][ROLL][MIN] = 0;
  rot[HEAD][CENTER][ROLL][MAX] = 0;
  rot[HEAD][CENTER][ROLL][CURRENT] = 0;
  rot[HEAD][CENTER][PITCH][MIN] = 0;
  rot[HEAD][CENTER][PITCH][MAX] = 0;
  rot[HEAD][CENTER][PITCH][CURRENT] = 0;
  rot[HEAD][CENTER][YAW][MIN] = 0;
  rot[HEAD][CENTER][YAW][MAX] = 0;
  rot[HEAD][CENTER][YAW][CURRENT] = 0;
  rot[HEAD][NECK][ROLL][MIN] = 0;
  rot[HEAD][NECK][ROLL][MAX] = 0;
  rot[HEAD][NECK][ROLL][CURRENT] = 0;
  rot[HEAD][NECK][PITCH][MIN] = -38.5 * rad;
  rot[HEAD][NECK][PITCH][MAX] = 29.5 * rad;
  rot[HEAD][NECK][PITCH][CURRENT] = 0;
  rot[HEAD][NECK][YAW][MIN] = -119.5 * rad;
  rot[HEAD][NECK][YAW][MAX] = 119.5 * rad;
  rot[HEAD][NECK][YAW][CURRENT] = 0;
  rot[HEAD][LASER][ROLL][MIN] = 0;
  rot[HEAD][LASER][ROLL][MAX] = 0;
  rot[HEAD][LASER][ROLL][CURRENT] = 0;
  rot[HEAD][LASER][PITCH][MIN] = 0;
  rot[HEAD][LASER][PITCH][MAX] = 0;
  rot[HEAD][LASER][PITCH][CURRENT] = 0;
  rot[HEAD][LASER][YAW][MIN] = 0;
  rot[HEAD][LASER][YAW][MAX] = 0;
  rot[HEAD][LASER][YAW][CURRENT] = 0;
  
  rot[LEFT][CENTER][ROLL][MIN] = 0;
  rot[LEFT][CENTER][ROLL][MAX] = 0;
  rot[LEFT][CENTER][ROLL][CURRENT] = 0;
  rot[LEFT][CENTER][PITCH][MIN] = 0;
  rot[LEFT][CENTER][PITCH][MAX] = 0;
  rot[LEFT][CENTER][PITCH][CURRENT] = 0;
  rot[LEFT][CENTER][YAW][MIN] = 0;
  rot[LEFT][CENTER][YAW][MAX] = 0;
  rot[LEFT][CENTER][YAW][CURRENT] = 0;
  rot[LEFT][SHOULDER][ROLL][MIN] = 0.5 * rad;
  rot[LEFT][SHOULDER][ROLL][MAX] = 94.5 * rad;
  rot[LEFT][SHOULDER][ROLL][CURRENT] = 0;
  rot[LEFT][SHOULDER][PITCH][MIN] = -119.5 * rad;
  rot[LEFT][SHOULDER][PITCH][MAX] = 119.5 * rad;
  rot[LEFT][SHOULDER][PITCH][CURRENT] = 0;
  rot[LEFT][SHOULDER][YAW][MIN] = 0;
  rot[LEFT][SHOULDER][YAW][MAX] = 0;
  rot[LEFT][SHOULDER][YAW][CURRENT] = 0;
  rot[LEFT][ELBOW][ROLL][MIN] = -89.5 * rad;
  rot[LEFT][ELBOW][ROLL][MAX] = -0.5 * rad;
  rot[LEFT][ELBOW][ROLL][CURRENT] = 0;
  rot[LEFT][ELBOW][PITCH][MIN] = 0;
  rot[LEFT][ELBOW][PITCH][MAX] = 0;
  rot[LEFT][ELBOW][PITCH][CURRENT] = 0;
  rot[LEFT][ELBOW][YAW][MIN] = -119.5 * rad;
  rot[LEFT][ELBOW][YAW][MAX] = 119.5 * rad;
  rot[LEFT][ELBOW][YAW][CURRENT] = 0;
  rot[LEFT][WRIST][ROLL][MIN] = 0;
  rot[LEFT][WRIST][ROLL][MAX] = 0;
  rot[LEFT][WRIST][ROLL][CURRENT] = 0;
  rot[LEFT][WRIST][PITCH][MIN] = 0;
  rot[LEFT][WRIST][PITCH][MAX] = 0;
  rot[LEFT][WRIST][PITCH][CURRENT] = 0;
  rot[LEFT][WRIST][YAW][MIN] = -104.5 * rad;
  rot[LEFT][WRIST][YAW][MAX] = 104.5 * rad;
  rot[LEFT][WRIST][YAW][CURRENT] = 0;
  rot[LEFT][HAND][ROLL][MIN] = 0;
  rot[LEFT][HAND][ROLL][MAX] = 0;
  rot[LEFT][HAND][ROLL][CURRENT] = 0;
  rot[LEFT][HAND][PITCH][MIN] = 0;
  rot[LEFT][HAND][PITCH][MAX] = 0;
  rot[LEFT][HAND][PITCH][CURRENT] = 0;
  rot[LEFT][HAND][YAW][MIN] = 0;
  rot[LEFT][HAND][YAW][MAX] = 0;
  rot[LEFT][HAND][YAW][CURRENT] = 0;

  rot[RIGHT][CENTER][ROLL][MIN] = 0;
  rot[RIGHT][CENTER][ROLL][MAX] = 0;
  rot[RIGHT][CENTER][ROLL][CURRENT] = 0;
  rot[RIGHT][CENTER][PITCH][MIN] = 0;
  rot[RIGHT][CENTER][PITCH][MAX] = 0;
  rot[RIGHT][CENTER][PITCH][CURRENT] = 0;
  rot[RIGHT][CENTER][YAW][MIN] = 0;
  rot[RIGHT][CENTER][YAW][MAX] = 0;
  rot[RIGHT][CENTER][YAW][CURRENT] = 0;
  rot[RIGHT][SHOULDER][ROLL][MIN] = -94.5 * rad;
  rot[RIGHT][SHOULDER][ROLL][MAX] = -0.5 * rad;
  rot[RIGHT][SHOULDER][ROLL][CURRENT] = 0;
  rot[RIGHT][SHOULDER][PITCH][MIN] = -119.5 * rad;
  rot[RIGHT][SHOULDER][PITCH][MAX] = 119.5 * rad;
  rot[RIGHT][SHOULDER][PITCH][CURRENT] = 0;
  rot[RIGHT][SHOULDER][YAW][MIN] = 0;
  rot[RIGHT][SHOULDER][YAW][MAX] = 0;
  rot[RIGHT][SHOULDER][YAW][CURRENT] = 0;
  rot[RIGHT][ELBOW][ROLL][MIN] = 0.5 * rad;
  rot[RIGHT][ELBOW][ROLL][MAX] = 89.5 * rad;
  rot[RIGHT][ELBOW][ROLL][CURRENT] = 0;
  rot[RIGHT][ELBOW][PITCH][MIN] = 0;
  rot[RIGHT][ELBOW][PITCH][MAX] = 0;
  rot[RIGHT][ELBOW][PITCH][CURRENT] = 0;
  rot[RIGHT][ELBOW][YAW][MIN] = -119.5 * rad;
  rot[RIGHT][ELBOW][YAW][MAX] = 119.5 * rad;
  rot[RIGHT][ELBOW][YAW][CURRENT] = 0;
  rot[RIGHT][WRIST][ROLL][MIN] = 0;
  rot[RIGHT][WRIST][ROLL][MAX] = 0;
  rot[RIGHT][WRIST][ROLL][CURRENT] = 0;
  rot[RIGHT][WRIST][PITCH][MIN] = 0;
  rot[RIGHT][WRIST][PITCH][MAX] = 0;
  rot[RIGHT][WRIST][PITCH][CURRENT] = 0;
  rot[RIGHT][WRIST][YAW][MIN] = -104.5 * rad;
  rot[RIGHT][WRIST][YAW][MAX] = 104.5 * rad;
  rot[RIGHT][WRIST][YAW][CURRENT] = 0;
  rot[RIGHT][HAND][ROLL][MIN] = 0;
  rot[RIGHT][HAND][ROLL][MAX] = 0;
  rot[RIGHT][HAND][ROLL][CURRENT] = 0;
  rot[RIGHT][HAND][PITCH][MIN] = 0;
  rot[RIGHT][HAND][PITCH][MAX] = 0;
  rot[RIGHT][HAND][PITCH][CURRENT] = 0;
  rot[RIGHT][HAND][YAW][MIN] = 0;
  rot[RIGHT][HAND][YAW][MAX] = 0;
  rot[RIGHT][HAND][YAW][CURRENT] = 0;
}


/*
batch draw_rotors()
{
  // Draw the rotation directions as 2-blades
  dynamic{NeckRotation1 = Neck ^ (Neck . (ni ^ e1 ^ e2)),};
  dynamic{NeckRotation2 = Neck ^ (Neck . (ni ^ e1 ^ e3)),};

  dynamic{LShoulderRotation1 = LShoulder ^ (LShoulder . (ni ^ e1 ^ e2)),};
  dynamic{LShoulderRotation2 = LShoulder ^ (LShoulder . (ni ^ e2 ^ e3)),};

  dynamic{LElbowRotation1 = LElbow ^ (LElbow . (ni ^ e1 ^ e2)),};
  dynamic{LElbowRotation2 = LElbow ^ (LElbow . (ni ^ e2 ^ e3)),};

  dynamic{LWristRotation = LWrist ^ (LWrist . (ni ^ e2 ^ e3)),};

  dynamic{RShoulderRotation1 = RShoulder ^ (RShoulder . (ni ^ e1 ^ e2)),};
  dynamic{RShoulderRotation2 = RShoulder ^ (RShoulder . (ni ^ e2 ^ e3)),};

  dynamic{RElbowRotation1 = RElbow ^ (RElbow . (ni ^ e1 ^ e2)),};
  dynamic{RElbowRotation2 = RElbow ^ (RElbow . (ni ^ e2 ^ e3)),};

  dynamic{RWristRotation = RWrist ^ (RWrist . (ni ^ e2 ^ e3)),};
}
*/


batch generate_distances() {
  reach[HEAD] = 0;
  reach[LEFT] = 0;
  reach[RIGHT] = 0;

  // Define the distances between each joint d[i] = |p[i + 1] - p[i]| for i = 1, ..., chain_len
  for (i = 0; i < HEAD_SIZE - 1; i = i + 1) {
    d[HEAD][i] = distance(KChain[HEAD][i + 1], KChain[HEAD][i]);
    reach[HEAD] = reach[HEAD] + d[HEAD][i];
  }
  reach[HEAD] = reach[HEAD] + d[HEAD][HEAD_SIZE - 1];

  for (i = 0; i < LEFT_SIZE - 1; i = i + 1) {
    d[LEFT][i] = distance(KChain[LEFT][i + 1], KChain[LEFT][i]);
    reach[LEFT] = reach[LEFT] + d[LEFT][i];
  }
  reach[LEFT] = reach[LEFT] + d[LEFT][LEFT_SIZE - 1];

  for (i = 0; i < RIGHT_SIZE - 1; i = i + 1) {
    d[RIGHT][i] = distance(KChain[RIGHT][i + 1], KChain[RIGHT][i]);
    reach[RIGHT] = reach[RIGHT] + d[RIGHT][i];
  }
  reach[RIGHT] = reach[RIGHT] + d[RIGHT][RIGHT_SIZE - 1];
}


function fabrik(chain_nr, chain_size, target) {
  // The distance between root and target.
  dist = distance(::KChain[chain_nr][0], target);
  print(dist);
  // Check whether the target is within reach.
  if (dist > ::reach[chain_nr]) {
    // The target is unreachable.
    cprint("Out of reach!");
    for (i = 0; i < chain_size - 1; i = i + 1) {
      // Find the distance between the target and each joint's position.
      r = distance(target, ::KChain[chain_nr][i]);
      lambda = ::d[chain_nr][i] / r;
      // Find the new joint positions.
      ::KChain[chain_nr][i + 1] = wavg(1 - lambda, ::KChain[chain_nr][i], lambda, target);
    }
  }
  else {
    cprint("Target is reachable");
    // The target is reachable; thus, set as b the initial position of the
    // first joint.
    b = ::KChain[chain_nr][0];
    dif_A = distance(::KChain[chain_nr][chain_size - 1], target);
    while (dif_A > ::TOLERANCE) {
      cprint("Forward reaching");
      // STAGE 1: FORWARD REACHING
      // Set the end effector as target.
      ::KChain[chain_nr][chain_size - 1] = target;
      for (i = chain_size - 2; i >= 0; i = i - 1) {
        // Find the distance between the target and each joint's position.
        r_i = distance(::KChain[chain_nr][i + 1], ::KChain[chain_nr][i]);
        lambda = ::d[chain_nr][i] / r_i;
        // Find the new joint positions.
        ::KChain[chain_nr][i] = wavg(1 - lambda, ::KChain[chain_nr][i + 1], lambda, ::KChain[chain_nr][i]);
      }
      cprint("Backward reaching");
      // STAGE 2: BACKWARD REACHING
      // Set the root to its initial position.
      ::KChain[chain_nr][0] = b;
      for (i = 0; i < chain_size - 1; i = i + 1) {
        // Find the distance between the target and each joint's position.
        r_i = distance(::KChain[chain_nr][i + 1], ::KChain[chain_nr][i]);
        lambda = ::d[chain_nr][i] / r_i;
        // Find the new joint positions.
        ::KChain[chain_nr][i + 1] = wavg(1 - lambda, ::KChain[chain_nr][i], lambda, ::KChain[chain_nr][i + 1]);
      }

      dif_A = distance(::KChain[chain_nr][chain_size - 1], target);
    }
  }
}


function constrain_orientation(rotor, chain1, joint1, chain2, joint2) {
  // if orientation is outside the bounds of joint1, reorient joint1 in such a
  // way that the rotor will be within the limits.
  if (orientation < ::rot[chain1][joint1][MIN]) {
  }
  else if (orientation > ::rot[chain1][joint1][MAX]) {
  }

  return rotor;
}


// HELPER FUNCTIONS
function draw_line(p1, p2) {
  point_pair = dm4(c3ga_point(p1) ^ c3ga_point(p2)),
  return point_pair;
}


function pt(x) {
  return x;
}


function wavg(w1, p1, w2, p2) {
// Weighted average
  return (w1 * p1 + w2 * p2) / (w1 + w2);
}


function distance(x, y) {
  //diff = x - y;
  //return sqrt(diff . diff);

  //return norm((e3ga) (x - y));

  return norm(x - y);
}
